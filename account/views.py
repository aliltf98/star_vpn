import os
import sys

from django.contrib.auth.models import User
from django.db.models import Q

from account.models import UserProfile

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect

from services.PanelManager import PanelManager
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


def subscription(request, username):
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
