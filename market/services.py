import time
from datetime import timedelta
from django.db import transaction
from django.utils import timezone
from account.models import UserProfile
from main.models import MainPlansLayout
from .models import Order, Commission, MarketerProfile, UserSubscription
from services.PanelManager import PanelManager


class OrderService:

    @staticmethod
    def create_order(user, plan_id, gateway_name='manual'):
        try:
            plan = MainPlansLayout.objects.get(id=plan_id)
        except MainPlansLayout.DoesNotExist:
            return None, "پلن انتخاب‌شده معتبر نیست."

        plan_price = plan.price
        discount_amount = 0

        # بررسی وجود معرف برای کاربر
        user_profile = getattr(user, 'profile', None)
        marketer = user_profile.referred_by if user_profile else None

        # اگر کاربر معرف فعال داشته باشد و خودش بازاریاب خود نباشد
        if marketer and marketer.is_active and marketer.user != user:
            discount_amount = (plan_price * marketer.discount_rate) / 100

        final_amount = plan_price - discount_amount

        # بررسی خرید اول بودن کاربر
        is_first_order = not Order.objects.filter(user=user, status=Order.StatusChoices.COMPLETED).exists()

        # ثبت سفارش در حالت انتظار
        order = Order.objects.create(
            user=user,
            plan=plan,
            plan_price=plan_price,
            discount_amount=discount_amount,
            final_amount=final_amount,
            is_first_order=is_first_order,
            gateway_name=gateway_name,
            status=Order.StatusChoices.PENDING
        )

        return order, None


class PaymentProcessingService:

    @staticmethod
    @transaction.atomic
    def process_successful_order(order: Order, ref_id: str = None):
        """
        پردازش سفارش موفق:
        ۱. تغییر وضعیت سفارش
        ۲. اعمال تغییرات مستقیم در پنل مرزبان (تأمین حجم و زمان)
        ۳. به‌روزرسانی/ثبت اشتراک کاربر در دیتابیس local (UserSubscription)
        ۴. محاسبه و واریز پورسانت بازاریاب
        """
        if order.status == Order.StatusChoices.COMPLETED:
            return True, "این سفارش قبلاً پردازش شده است."

        # ۱. به‌روزرسانی وضعیت سفارش
        order.status = Order.StatusChoices.COMPLETED
        if ref_id:
            order.ref_id = ref_id
        order.save()

        user = order.user
        plan = order.plan
        username = user.username

        # ۲. همگام‌سازی و فعال‌سازی در پنل مرزبان
        now_timestamp = int(time.time())
        user_info = PanelManager.get_user_info(username)

        if user_info and isinstance(user_info, dict) and 'username' in user_info:
            # کاربر وجود دارد -> افزودن حجم باقی‌مانده + زمان از بالاترین تاریخ انقضا
            used_bytes = user_info.get('used_traffic', 0) or 0
            limit_bytes = user_info.get('data_limit', 0) or 0
            remaining_bytes = max(0, limit_bytes - used_bytes)
            current_data_gb = remaining_bytes / (1024 ** 3)

            new_total_data_gb = current_data_gb + plan.volume_gb

            current_expire = user_info.get('expire') or 0
            base_expire = max(now_timestamp, current_expire)
            new_expire = base_expire + (plan.duration_days * 86400)

            PanelManager.modify_user(username, data_limit_gb=new_total_data_gb, expire_timestamp=new_expire)
            expire_dt = timezone.datetime.fromtimestamp(new_expire, tz=timezone.utc)
        else:
            # کاربر وجود ندارد -> ساخت جدید
            new_expire = now_timestamp + (plan.duration_days * 86400)
            PanelManager.create_user(username, data_limit_gb=plan.volume_gb, expire_timestamp=new_expire)
            expire_dt = timezone.datetime.fromtimestamp(new_expire, tz=timezone.utc)

        # ۳. فعال‌سازی یا تمدید رکورد local اشتراک دیتابیس
        subscription, created = UserSubscription.objects.get_or_create(
            user=user,
            defaults={
                'plan': plan,
                'order': order,
                'expire_date': expire_dt,
                'total_volume_gb': plan.volume_gb,
                'is_active': True
            }
        )

        if not created:
            subscription.plan = plan
            subscription.order = order
            subscription.expire_date = expire_dt
            subscription.total_volume_gb += plan.volume_gb
            subscription.is_active = True
            subscription.save()

        # ۴. محاسبه و واریز کمیسیون بازاریاب
        PaymentProcessingService._apply_commission(order)

        return True, "اشتراک با موفقیت در مرزبان و سیستم فعال شد."

    @staticmethod
    def _apply_commission(order: Order):
        """محاسبه دقیق پورسانت خرید اول یا تمدید و واریز به کیف پول بازاریاب"""
        try:
            user_profile = getattr(order.user, 'profile', None)
        except Exception:
            return

        if not user_profile:
            return

        marketer = user_profile.referred_by

        # اگر کاربر معرفی نداشته باشد یا حساب نماینده غیرفعال باشد
        if not marketer or not marketer.is_active:
            return

        # جلوگیری از خود-ارجاعی (Self-Referral)
        if marketer.user == order.user:
            return

        # تعیین نوع خرید و نرخ پورسانت
        if order.is_first_order:
            commission_type = Commission.CommissionTypes.FIRST_ORDER
            rate = marketer.first_order_commission_rate
        else:
            commission_type = Commission.CommissionTypes.RENEWAL
            rate = marketer.renewal_commission_rate

        # محاسبه مبلغ پورسانت از روی final_amount پرداختی
        commission_amount = (order.final_amount * rate) / 100

        # ثبت رکورد کمیسیون (در صورت عدم وجود از قبل)
        Commission.objects.get_or_create(
            order=order,
            defaults={
                'marketer': marketer,
                'commission_type': commission_type,
                'order_amount': order.final_amount,
                'commission_amount': commission_amount,
                'applied_rate': rate,
                'status': Commission.StatusChoices.APPROVED
            }
        )

        # شارژ کیف پول بازاریاب
        marketer.wallet_balance += commission_amount
        marketer.save()