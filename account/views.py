import os
import sys

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from market.models import *

from django.contrib.auth.models import User
from django.db.models import Q

from account.models import UserProfile

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect


import datetime
import time
from django.utils import timezone
from services.PanelManager import PanelManager  # ایمپورت پلتفرم مرزبان
from services.models import ServiceProfile


# Create your views here.

def register(request):
    # دریافت پارامتر next از URL (برای متد GET) یا از فرم (برای متد POST)
    next_url = request.POST.get('next') or request.GET.get('next')

    if request.method == 'POST':
        regtype = request.POST.get('reg')
        username = request.POST.get('username', '').strip()
        pass1 = request.POST.get('pass1')

        # تعیین مقصد نهایی پس از ورود یا ثبت‌نام موفق
        redirect_target = next_url if next_url else '/'

        if regtype == "signin":
            user = None
            usr = None

            if UserProfile.objects.filter(profile__username=username).exists():
                usr = UserProfile.objects.select_related('profile').get(profile__username=username)

            elif username.isdigit() and UserProfile.objects.filter(phone_number=username).exists():
                usr = UserProfile.objects.select_related('profile').get(phone_number=username)

            if usr:
                user = authenticate(request, username=usr.profile.username, password=pass1)

            if user is None:
                messages.error(request, 'حساب کاربری یا کلمه عبور اشتباه است')
                # حفظ آدرس next در صورت بروز خطا
                return redirect(f"{request.path}?next={next_url}" if next_url else 'register')
            else:
                login(request, user)
                messages.success(request, "ورود با موفقیت انجام شد.")
                return redirect(redirect_target)

        elif regtype == "signup":
            pass2 = request.POST.get('pass2')
            phone_number = request.POST.get('number', '').strip()

            if User.objects.filter(username=username).exists():
                messages.error(request, "این حساب کاربری قبلا ساخته شده")
                return redirect(f"{request.path}?next={next_url}" if next_url else 'register')

            if phone_number.isdigit() and UserProfile.objects.filter(phone_number=phone_number).exists():
                messages.error(request, "این شماره تلفن قبلا ثبت شده است")
                return redirect(f"{request.path}?next={next_url}" if next_url else 'register')

            if pass1 != pass2:
                messages.error(request, "رمز ها همخوانی ندارند")
                return redirect(f"{request.path}?next={next_url}" if next_url else 'register')

            user = User.objects.create_user(username=username, password=pass1)
            UserProfile.objects.create(
                profile=user,
                phone_number=int(phone_number) if phone_number.isdigit() else None,
            )

            # ورود خودکار کاربر پس از ثبت‌نام
            login(request, user)
            messages.success(request, 'حساب کاربری شما با موفقیت ساخته شد')
            return redirect(redirect_target)

        else:
            return redirect('register')

    return render(request, "registration.html", {'next': next_url})


def signout(request):
    try:
        logout(request)
        messages.error(request, "با موفقیت خارج شدید")
    except Exception as e:
        messages.error(request, str(e))
        print(e)
    return redirect("/")


def humanbytes(B):
    B = float(B)
    KB = float(1024)
    MB = float(KB ** 2)
    GB = float(KB ** 3)
    TB = float(KB ** 4)

    if B < KB:
        return '{0} {1}'.format(B,'Bytes' if 0 == B > 1 else 'Byte')
    elif KB <= B < MB:
        return '{0:.2f} KB'.format(B / KB)
    elif MB <= B < GB:
        return '{0:.2f} MB'.format(B / MB)
    elif GB <= B < TB:
        return '{0:.2f} GB'.format(B / GB)
    elif TB <= B:
        return '{0:.2f} TB'.format(B / TB)


def subscription(request):
    username = request.user.username
    # ۱. بررسی لاگین بودن کاربر
    if not request.user.is_authenticated:
        return render(request, "subscription.html", {
            "require_login": True
        })

    # ۲. بررسی وجود کاربر در دیتابیس جنگو
    try:
        target_user = User.objects.get(username=username)
    except User.DoesNotExist:
        return render(request, "subscription.html", {
            "user_not_found": True
        })

    # ۳. بررسی دسترسی (فقط خود کاربر یا Superuser اجازه مشاهده دارند)
    if request.user != target_user and not request.user.is_superuser:
        return render(request, "subscription.html", {
            "permission_denied": True
        })

    # ۴. دریافت اطلاعات از پنل
    panel_info = PanelManager.get_user_info(username)

    if not panel_info:
        return render(request, "subscription.html", {
            "user_not_found": True
        })

    devices_data = []
    try:
        service_prof = ServiceProfile.objects.filter(profile__profile__username=username).first()

        if service_prof:
            for conn in service_prof.connections.all():
                devices_data.append({
                    "device_id": conn.device_id,
                    "model_name": conn.model_name,
                    "is_blocked": conn.is_blocked,
                    "traffic_used": humanbytes(conn.traffic_used)
                })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print("Error fetching devices:", e)

    context = {
        "target_user": target_user.username,
        "expire": panel_info.get('expire'),
        "data_limit": humanbytes(panel_info.get('data_limit', 0)),
        "note": panel_info.get('note'),
        "status": panel_info.get('status'),
        "used_traffic": humanbytes(panel_info.get('lifetime_used_traffic', 0)),
        "devices": devices_data,
    }

    return render(request, "subscription.html", context)

@login_required
def dashboard_view(request):
    user = request.user
    context = {}

    # اضافه کردن لیست تمام پلن‌ها به context برای استفاده در مودال «افزودن کاربر»
    context['available_plans'] = MainPlansLayout.objects.all()

    # ۱. بررسی دسترسی ادمین (Superuser)
    if user.is_superuser:
        context['user_role'] = 'admin'

    # ۲. بررسی اینکه آیا کاربر فروشنده (دارای پروفایل مارکتر) است یا خیر
    elif hasattr(user, 'marketer_profile'):
        marketer = user.marketer_profile
        context['user_role'] = 'seller'
        context['marketer_profile'] = marketer

        # لیست کاربرانی که توسط این فروشنده دعوت شده‌اند همراه با محاسبه تعداد تمدیدها و آخرین پلن فعال
        referred_users = marketer.referred_users.select_related('profile').annotate(
            # شمارش تعداد سفارشات/تمدیدهای موفق هر کاربر
            calculated_renewal_count=Count(
                'profile__orders',
                filter=Q(profile__orders__status=Order.StatusChoices.COMPLETED)
            )
        ).all()

        # برای هر کاربر در لیست، پلن فعلی‌اش را هم استخراج می‌کنیم
        enriched_referred_users = []
        for ref in referred_users:
            active_sub = getattr(ref.profile, 'subscriptions', None)
            active_plan = active_sub.filter(is_active=True).first() if active_sub else None

            enriched_referred_users.append({
                'profile': ref.profile,
                'renewal_count': ref.calculated_renewal_count,
                'active_plan': active_plan.plan.title if (active_plan and hasattr(active_plan, 'plan')) else (
                    active_plan.title if active_plan else 'بدون پلن فعال')
            })

        context['referred_users'] = enriched_referred_users
        referred_user_users = [ref['profile'] for ref in enriched_referred_users]

        # محاسبه داده‌های نمودار فروش
        sales_chart_data = (
            Order.objects.filter(user__in=referred_user_users, status=Order.StatusChoices.COMPLETED)
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(total_sales=Count('id'), total_revenue=Sum('final_amount'))
            .order_by('month')
        )
        context['sales_chart_data'] = list(sales_chart_data)

    # ۳. کاربر عادی سیستم
    else:
        context['user_role'] = 'regular'

        # دریافت پروفایل کاربری و اشتراک فعال از دیتابیس
        user_profile = getattr(user, 'profile', None)
        active_subscription = user.subscriptions.filter(is_active=True).first()

        context['user_profile'] = user_profile
        context['active_subscription'] = active_subscription

        # دریافت اطلاعات از پنل (مشابه تابع subscription)
        panel_info = PanelManager.get_user_info(user.username)

        if panel_info:
            context['expire'] = panel_info.get('expire')
            context['data_limit'] = humanbytes(panel_info.get('data_limit', 0))
            context['note'] = panel_info.get('note')
            context['status'] = panel_info.get('status')
            context['used_traffic'] = humanbytes(panel_info.get('lifetime_used_traffic', 0))

        # استخراج لیست دستگاه‌های متصل (مشابه تابع subscription)
        devices_data = []
        try:
            service_prof = ServiceProfile.objects.filter(profile__profile__username=user.username).first()
            if service_prof:
                for conn in service_prof.connections.all():
                    devices_data.append({
                        "device_id": conn.device_id,
                        "model_name": conn.model_name,
                        "is_blocked": conn.is_blocked,
                        "traffic_used": humanbytes(conn.traffic_used)
                    })
        except Exception as e:
            print("Error fetching devices in dashboard:", e)

        context['devices'] = devices_data

    print(context)
    return render(request, 'dashboard/index.html', context)


@login_required
def profile_view(request):
    user = request.user
    # دریافت یا ایجاد پروفایل کاربری
    profile = UserProfile.objects.get(profile=user)

    # بررسی اینکه آیا کاربر مارکتر (فروشنده) هست یا خیر
    # با توجه به related_name='marketer_profile'
    marketer_profile = getattr(user, 'marketer_profile', None)

    if request.method == 'POST':
        # دریافت اطلاعات از فرم
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')

        # به‌روزرسانی اطلاعات مدل پیش‌فرض User
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()

        # به‌روزرسانی اطلاعات UserProfile
        profile.phone_number = phone_number
        profile.save()

        # اگر کاربر مارکتر بود، اطلاعات بانکی‌اش هم آپدیت شود
        if marketer_profile:
            marketer_profile.card_number = request.POST.get('card_number')
            marketer_profile.shaba_number = request.POST.get('shaba_number')
            marketer_profile.bank_name = request.POST.get('bank_name')
            marketer_profile.save()

        messages.success(request, 'اطلاعات پروفایل با موفقیت به‌روزرسانی شد.')
        return redirect('profile')  # نام آدرس (URL name) صفحه پروفایل خود را اینجا قرار دهید

    context = {
        'profile': profile,
        'marketer_profile': marketer_profile,
    }
    return render(request, 'dashboard/partials/profile.html', context)

@login_required
@transaction.atomic  # تضمین امنیت تراکنش دیتابیس
def newUser(request):
    if request.method == 'POST':
        input_username = request.POST.get('username')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')
        plan_id = request.POST.get('plan_id')
        has_dashboard_access = request.POST.get('has_dashboard_access') == 'true'

        # ۱. بررسی پروفایل مارکترِ کاربرِ درخواست‌دهنده
        marketer = getattr(request.user, 'marketer_profile', None)

        # ۲. ساخت نام کاربری نهایی با احتساب کد معرف (اگر سازنده مارکتر باشد)
        final_username = input_username
        if marketer:
            final_username = f"{marketer.code}{input_username}"

        # ۳. اعتبارسنجی دقیق تکراری نبودن نام کاربری نهایی
        if User.objects.filter(username=final_username).exists():
            messages.error(request, 'این نام کاربری قبلاً ثبت شده است.')
            return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

        try:
            # ۴. دریافت پلن انتخابی و بررسی سقف بدهی مجاز کیف پول مارکتر (تا ۷ میلیون منفی)
            selected_plan = None
            plan_price = 0
            if plan_id:
                try:
                    selected_plan = MainPlansLayout.objects.get(id=plan_id)
                    plan_price = selected_plan.price
                except MainPlansLayout.DoesNotExist:
                    pass

            if marketer and selected_plan:
                projected_balance = marketer.wallet_balance - plan_price
                if projected_balance < -7000000:
                    messages.error(request, 'سقف مجاز بدهی کیف پول شما (منفی ۷ میلیون تومان) تکمیل شده است و امکان ثبت این پلن وجود ندارد.')
                    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

            # تعیین حجم و مدت‌زمان پلن
            plan_volume = selected_plan.volume_gb if selected_plan else 10
            plan_duration_days = selected_plan.duration_days if (
                    selected_plan and hasattr(selected_plan, 'duration_days')) else 30

            # ۵. ایجاد کاربر در پنل مرزبان (Marzban)
            now_timestamp = int(time.time())
            expire_timestamp = now_timestamp + (plan_duration_days * 86400)

            marzban_response = PanelManager.create_user(
                username=final_username,
                data_limit_gb=plan_volume,
                expire_timestamp=expire_timestamp
            )

            if not marzban_response:
                print("marzban")
                messages.error(request, 'خطا در ارتباط با پنل مرزبان؛ کاربر ایجاد نشد.')
                return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

            # ۶. ساخت کاربر در دیتابیس محلی جنگو
            user = User.objects.create_user(
                username=final_username,
                password=password
            )
            user.is_staff = has_dashboard_access
            user.save()

            # ۷. ساخت پروفایل کاربری و اتصال به مارکتر
            UserProfile.objects.create(
                profile=user,
                phone_number=phone_number,
                referred_by=marketer
            )

            # ۸. اگر پلنی انتخاب شده باشد: ثبت سفارش، منفی شدن/کسر از کیف پول و ایجاد اشتراک
            if selected_plan:
                print(1)
                expire_dt = datetime.datetime.fromtimestamp(expire_timestamp, tz=datetime.timezone.utc)
                subscription_url = marzban_response.get('subscription_url')
                print(2)

                # ثبت سفارش تکمیل‌شده برای کاربر جدید
                order = Order.objects.create(
                    user=user,
                    plan=selected_plan,
                    plan_price=plan_price,
                    discount_amount=0,
                    final_amount=plan_price,
                    is_first_order=True,
                    status=Order.StatusChoices.COMPLETED,
                    gateway_name='market'
                )
                print(3)
                # کسر هزینه از کیف پول مارکتر (اجازه ورود به محدوده منفی تا ۷ میلیون)
                if marketer:
                    marketer.wallet_balance -= plan_price
                    marketer.save()
                    print(4)
                print(5)

                # ثبت اشتراک محلی (UserSubscription) با اتصال به سفارش و لینک اشتراک مرزبان
                UserSubscription.objects.create(
                    user=user,
                    plan=selected_plan,
                    order=order,
                    expire_date=expire_dt,
                    total_volume_gb=plan_volume,
                    is_active=True,
                    subscription_url=subscription_url
                )
                print(6)

            messages.success(request, 'کاربر جدید و اشتراک او با موفقیت ایجاد شد.')

        except Exception as e:
            print(e)

            messages.error(request, f'خطا در ایجاد کاربر: {e}')

    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))