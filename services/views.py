import os
import sys

from django.contrib.auth import authenticate
from django.db import transaction
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .PanelManager import PanelManager
from .serializers import *


class Signup(APIView):
    def post(self, request):
        try:
            serializer = SignupSerializer(data=request.data)
            print("SignUp API started")
            print(request.data)
            if serializer.is_valid():
                v_data = serializer.validated_data  # استفاده از داده‌های تایید شده

                if User.objects.filter(username=v_data['username']).exists():
                    return Response({'message': 'این نام کاربری قبلاً انتخاب شده'}, status=status.HTTP_400_BAD_REQUEST)

                with transaction.atomic():  # تضمین سلامت دیتابیس
                    user = User.objects.create_user(
                        username=v_data['username'],
                        password=v_data['password'],
                    )
                    UserProfile.objects.create(
                        profile=user,
                        phone_number=v_data['number'],
                    )

                return Response({'message': "حساب کاربری با موفقیت ساخته شد"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(1,e)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Signin(APIView):
    def post(self, request):
        # try:
            # print(request.data)
            # دریافت اطلاعات گوشی از بدنه درخواست (Request Body)
            # device_id = request.data.get('device_id')
            # model_name = request.data.get('model_name')
            #
            # serializer = SigninSerializer(data=request.data)
            # if serializer.is_valid():
            #     username = serializer.validated_data.get('username')
            #     password = serializer.validated_data.get('password')
            #
            #     user = None
            #     بررسی لاگین با نام کاربری یا شماره تلفن
                # if UserProfile.objects.filter(profile__username=username).exists():
                #     user = authenticate(request, username=username, password=password)
                # elif UserProfile.objects.filter(phone_number=username).exists():
                #     usr = UserProfile.objects.get(phone_number=username)
                #     user = authenticate(request, username=usr.profile.username, password=password)
                #
                # if user is None:
                #     return Response({"message": "حساب کاربری یا کلمه عبور اشتباه است"},
                #                     status=status.HTTP_400_BAD_REQUEST)
                #
                # ۱. تولید یا دریافت توکن
                # token, _ = Token.objects.get_or_create(user=user)
                #
                # ۲. مدیریت اطلاعات گوشی (Connection)
                # اگر device_id فرستاده شده بود، آن را ثبت یا بروزرسانی کن
                # configs_data = []
                # if device_id:
                #     connection, _ = Connection.objects.get_or_create(
                #         device_id=device_id,
                #         defaults={'model_name': model_name or "Unknown"}
                #     )
                #
                    # ۳. پیدا کردن ServiceProfile و کانفیگ‌ها
                #     service_prof = ServiceProfile.objects.filter(profile__profile__username=username).first()
                #     if service_prof:
                         # اضافه کردن گوشی به لیست اتصالات این پروفایل (اگر قبلاً نبود)
                #         if connection not in service_prof.connections.all():
                #             service_prof.connections.add(connection)
                #
                         # سریالایز کردن کانفیگ‌ها برای بازگشت به اندروید
                #         configs_serializer = UriCodeSerializer(service_prof.configs.all(), many=True)
                #         configs_data = configs_serializer.data

                # return Response({
                #     'token': token.key,
                #     'message': "ورود با موفقیت انجام شد",
                #     'configs': configs_data  # لیست کانفیگ‌ها در اینجا برمی‌گردد
                # }, status=status.HTTP_200_OK)
        #
        # except Exception as e:
        #     exc_type, exc_obj, exc_tb = sys.exc_info()
        #     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        #     print(exc_type, fname, exc_tb.tb_lineno)
        #     print(1, e)
        #     return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        try:
            # ۱. دریافت داده‌ها از اندروید
            username = request.data.get('username')
            password = request.data.get('password')
            device_id = request.data.get('device_id')
            model_name = request.data.get('model_name')
            user = None
            if UserProfile.objects.filter(profile__username=username).exists():
                user = authenticate(request, username=username, password=password)
            elif UserProfile.objects.filter(phone_number=username).exists():
                usr = UserProfile.objects.get(phone_number=username)
                user = authenticate(request, username=usr.profile.username, password=password)

            # ۲. احراز هویت (کاربری که قبلاً از سایت ثبت‌نام کرده)

            if not user:
                return Response({"message": "نام کاربری یا رمز عبور اشتباه است"}, status=status.HTTP_401_UNAUTHORIZED)

            # ۳. استعلام وضعیت کاربر از پنل Marzban
            panel_info = PanelManager.get_user_info(username)
            if not panel_info:
                return Response({"message": "سرویس شما در پنل یافت نشد"}, status=status.HTTP_404_NOT_FOUND)

            if panel_info.get('status') != 'active':
                return Response({"message": "اکانت شما غیرفعال یا منقضی شده است"}, status=status.HTTP_403_FORBIDDEN)

            # ۴. مدیریت توکن و ثبت دستگاه
            token, _ = Token.objects.get_or_create(user=user)
            # (در اینجا می‌توانید منطق ثبت Connection را که قبلاً نوشتیم اجرا کنید)

            # ۵. آماده‌سازی خروجی برای اندروید
            links = panel_info.get('links', [])
            total_limit = panel_info.get('data_limit', 0)
            used_traffic = panel_info.get('used_traffic', 0)
            print("ta inja okaye")
            # تبدیل بایت به گیگابایت
            remaining_gb = round((total_limit - used_traffic) / (1024 ** 3), 2) if total_limit else 0
            print(total_limit)
            print(used_traffic)
            print(remaining_gb)
            if device_id:
                connection, _ = Connection.objects.get_or_create(
                    device_id=device_id,
                    defaults={'model_name': model_name or "Unknown"}
                )


                # ۳. پیدا کردن ServiceProfile و کانفیگ‌ها
                service_prof = ServiceProfile.objects.filter(profile__profile__username=username).first()
                if service_prof:
                    # اضافه کردن گوشی به لیست اتصالات این پروفایل (اگر قبلاً نبود)
                    if connection not in service_prof.connections.all():
                        service_prof.connections.add(connection)

                    # سریالایز کردن کانفیگ‌ها برای بازگشت به اندروید
                    configs_serializer = UriCodeSerializer(service_prof.configs.all(), many=True)
                    configs_data = configs_serializer.data

            configs = []
            for link in links:
                configs.append({
                    "value": link,
                    "category_name": "V2Ray",
                    "remainingVolume": remaining_gb
                })
            print(configs)

            return Response({
                'token': token.key,
                'configs': configs,
                'username': username,
                'message': "خوش آمدید"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(1, e)
            return Response({'error': 'خطای داخلی سرور'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)