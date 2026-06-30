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
    if request.method == 'POST':
        regtype = request.POST['reg']
        username = request.POST['username']
        pass1 = request.POST['pass1']

        if regtype == "signin":
            print(1)
            user = None
            if UserProfile.objects.filter(profile__username=username).exists():
                usr = UserProfile.objects.get(profile__username=username)
                user = authenticate(request, username=usr.profile, password=pass1)
            elif UserProfile.objects.filter(phone_number=username).exists():
                usr = UserProfile.objects.get(phone_number=username)
                user = authenticate(request, username=usr.profile, password=pass1)
            if user is None:
                messages.error(request, 'حساب کاربری یا کلمه عبور اشتباه است')
                return redirect('register')
            else:
                login(request, user)
                messages.success(request, "ورود با موفقیت.")
                return redirect('/')

        elif regtype == "signup":
            print(2)
            pass2 = request.POST['pass2']
            phone_number = request.POST['number']
            if UserProfile.objects.filter(profile__username=username):
                messages.error(request, "این حساب کاربری قبلا ساخته شده")
                return redirect('register')

            if pass1 != pass2:
                messages.error(request, "رمز ها همخوانی ندارند")
                return redirect('register')
            user = User.objects.create_user(username=username, password=pass1)

            profile = UserProfile.objects.create(
                profile=user,
                phone_number=phone_number,
            )

            profile.save()
            messages.success(request, 'حساب کاربری شما با موفقیت ساخته شد')
            return redirect('/')
        else:
            return redirect('register')

    return render(request, "registration.html")


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
    MB = float(KB ** 2) # 1,048,576
    GB = float(KB ** 3) # 1,073,741,824
    TB = float(KB ** 4) # 1,099,511,627,776

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
    panel_info = PanelManager.get_user_info(username)
    devices_data = []
    try:
        service_prof = ServiceProfile.objects.filter(profile__profile__username=username).first()

        if not service_prof:
            print("service profile not found")

        for conn in service_prof.connections.all():
            devices_data.append({
                "device_id": conn.device_id,
                "model_name": conn.model_name,
                "is_blocked": conn.is_blocked,
                "traffic_used": humanbytes(conn.traffic_used)
            })
    except Exception as e:
        print(e)
    context = {
        "user": username,
        "expire": panel_info['expire'],
        "data_limit": humanbytes(panel_info['data_limit']),
        "note": panel_info['note'],
        "status": panel_info['status'],
        "used_traffic": humanbytes(panel_info['lifetime_used_traffic']),
        'devices': devices_data,
    }
    print(context)

    return render(request, "subscription.html", context)
