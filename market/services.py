from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from account.models import UserProfile
from main.models import MainPlansLayout
from market.models import Order, Commission, MarketerProfile
from .models import UserSubscription
# در صورت وجود تابع ارتباط با پنل API VPN آن را اینپورت کنید
# from services.panel_api import PanelManager
from main.models import MainPlansLayout

class OrderService:

    @staticmethod
    def create_order(user, plan_id):
        try:
            plan = MainPlansLayout.objects.get(id=plan_id)
        except MainPlansLayout.DoesNotExist:
            return None, "پلن انتخاب‌شده معتبر نیست."

        plan_price = plan.price
        discount_amount = 0

        # بررسی وجود معرف برای کاربر
        user_profile = getattr(user, 'userprofile', None)
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
            status=Order.StatusChoices.PENDING
        )

        return order, None

class PaymentProcessingService:

    @staticmethod
    @transaction.atomic
    def process_successful_order(order: Order, ref_id: str):
        """
        پردازش سفارش موفق:
        ۱. تغییر وضعیت سفارش
        ۲. فعال‌سازی/تمدید اشتراک کاربر در دیتابیس و پنل VPN
        ۳. محاسبه و ثبت کمیسیون بازاریاب (در صورت وجود)
        """
        if order.status == Order.StatusChoices.COMPLETED:
            return True, "Order already processed."

        # ۱. به‌روزرسانی وضعیت سفارش
        order.status = Order.StatusChoices.COMPLETED
        order.ref_id = ref_id
        order.save()

        user = order.user
        plan = order.plan

        # ۲. فعال‌سازی یا تمدید اشتراک در دیتابیس (UserSubscription)
        subscription, created = UserSubscription.objects.get_or_create(
            user=user,
            defaults={
                'plan': plan,
                'expire_date': timezone.now() + timedelta(days=30), # فرضا مدت پلن ۳۰ روز است
                'is_active': True
            }
        )

        if not created:
            # اگر اشتراک قبلی هنوز منقضی نشده، تاریخ انقضای جدید از ادامه انقضای قبلی محاسبه می‌شود
            base_date = subscription.expire_date if subscription.expire_date > timezone.now() else timezone.now()
            subscription.plan = plan
            subscription.expire_date = base_date + timedelta(days=30)
            subscription.is_active = True
            subscription.save()

        # ۳. فراخوانی API پنل VPN جهت شارژ یا ایجاد اکانت
        # try:
        #     PanelManager.add_or_extend_user(username=user.username, days=30, volume_gb=plan.volume)
        # except Exception as e:
        #     # لاگ خطا در صورت عدم ارتباط با پنل
        #     print(f"VPN Panel Error: {e}")

        # ۴. محاسبه و واریز کمیسیون بازاریاب
        PaymentProcessingService._apply_commission(order)

        return True, "Subscription activated successfully."

    @staticmethod
    def _apply_commission(order: Order):
        """محاسبه دقیق پورسانت خرید اول یا تمدید و واریز به کیف پول بازاریاب"""
        try:
            user_profile = order.user.userprofile
        except UserProfile.DoesNotExist:
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

        # محاسبه مبلغ پورسانت از روی مبلغ final_amount پرداختی
        commission_amount = (order.final_amount * rate) / 100

        # ثبت رکورد کمیسیون
        Commission.objects.create(
            marketer=marketer,
            order=order,
            commission_type=commission_type,
            order_amount=order.final_amount,
            commission_amount=commission_amount,
            applied_rate=rate,
            status=Commission.StatusChoices.APPROVED
        )

        # شارژ کیف پول بازاریاب
        marketer.wallet_balance += commission_amount
        marketer.save()