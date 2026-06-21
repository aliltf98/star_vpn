import os
import sys
import urllib.parse
import re

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
        try:
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

            if not user:
                return Response({"message": "نام کاربری یا رمز عبور اشتباه است"}, status=status.HTTP_401_UNAUTHORIZED)

            panel_info = PanelManager.get_user_info(user.username)
            if not panel_info:
                return Response({"message": "سرویس شما در پنل یافت نشد"}, status=status.HTTP_404_NOT_FOUND)

            if panel_info.get('status') != 'active':
                return Response({"message": "اکانت شما غیرفعال یا منقضی شده است"}, status=status.HTTP_403_FORBIDDEN)

            token, _ = Token.objects.get_or_create(user=user)

            if device_id:
                connection, created = Connection.objects.get_or_create(
                    device_id=device_id,
                    defaults={'model_name': model_name or "Unknown"}
                )
                if not created and model_name:
                    connection.model_name = model_name
                    connection.save()

                user_profile = UserProfile.objects.filter(profile=user).first()
                if user_profile:
                    service_prof, _ = ServiceProfile.objects.get_or_create(profile=user_profile)
                    if connection not in service_prof.connections.all():
                        service_prof.connections.add(connection)

            links = panel_info.get('links', [])
            total_limit = panel_info.get('data_limit', 0)
            used_traffic = panel_info.get('used_traffic', 0)

            remaining_bytes = max(0, total_limit - used_traffic) if total_limit > 0 else 0
            remaining_gb = round(remaining_bytes / (1024 ** 3), 2) if total_limit else 0

            # Dictionary to map country abbreviations inside brackets to real country displays
            country_map = {
                "GE": "Germany",
                "NL": "Netherlands",
                "TR": "Turkey",
                "US": "United States",
                "FI": "Finland"
            }

            configs = []
            for index, link in enumerate(links):
                category = "V2Ray"
                if link.startswith("vless://"):
                    category = "VLESS"
                elif link.startswith("vmess://"):
                    category = "VMESS"
                elif link.startswith("trojan://"):
                    category = "Trojan"

                # 🌟 EXTRACTING SERVER NAME & COUNTRY FROM THE URL FRAGMENT
                parsed_url = urllib.parse.urlparse(link)
                fragment = parsed_url.fragment  # Gets the string after the '#'

                server_name = f"Server {index + 1}"
                country = "Unknown"

                if fragment:
                    # Decodes URL codes like %20 to spaces, %28 to '(', and %29 to ')'
                    decoded_fragment = urllib.parse.unquote(fragment) # e.g. "1-test_android (Ge)"

                    # Regex search to extract code inside parenthesis, like (Ge) or (Nl)
                    match = re.search(r'\((.*?)\)', decoded_fragment)
                    if match:
                        country_code = match.group(1).upper() # Converts "Ge" to "GE"
                        country = country_map.get(country_code, country_code)

                        # Clean the server name by removing the country brackets section
                        server_name = decoded_fragment.split(" (")[0]
                    else:
                        server_name = decoded_fragment

                # 🌟 Append variables directly into each specific server config object node!
                configs.append({
                    "id": index,
                    "value": link,
                    "category_name": category,
                    "remainingVolume": remaining_gb,
                    "server_name": server_name,  # 👈 Passed seamlessly to Flutter now!
                    "country": country            # 👈 Passed seamlessly to Flutter now!
                })
            print(configs)

            return Response({
                'token': token.key,
                'configs': configs, # Contains updated server names and countries per link
                'username': user.username,
                'data_limit': total_limit,
                'remaining_bytes': remaining_bytes,
                'message': "Welcome"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

            return Response({'error': f'internal server error{str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserVolumeStatus(APIView):
    """
    Endpoint: /api/v1/vpn-usage/<username>/
    """
    def get(self, request, username):
        try:
            panel_info = PanelManager.get_user_info(username)
            if not panel_info:
                return Response({"status": "error", "message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            total_limit = panel_info.get('data_limit', 0)
            used_traffic = panel_info.get('used_traffic', 0)
            remaining_bytes = max(0, total_limit - used_traffic) if total_limit > 0 else 0

            # 🌟 Keys precisely mirror your Kotlin data class variables
            return Response({
                "status": "success",
                "username": username,
                "data_limit": total_limit,
                "used_traffic": used_traffic,
                "remaining_bytes": remaining_bytes
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"status": "error", "message": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserProfileView(APIView):
    def get(self, request, username):
        try:
            # 🌟 Lookup profile cleanly via the username string passed from Android
            user_profile = UserProfile.objects.filter(profile__username=username).first()

            panel_info = PanelManager.get_user_info(username)
            if not panel_info:
                return Response({"error": "سرویس شما یافت نشد"}, status=status.HTTP_404_NOT_FOUND)

            return Response({
                "username": username,
                "phone_number": str(user_profile.phone_number) if user_profile else "بدون شماره",
                "subscription_url": panel_info.get("subscription_url", ""),
                "data_limit": panel_info.get("data_limit", 0),
                "used_traffic": panel_info.get("used_traffic", 0)
            }, status=status.HTTP_200_OK)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeviceSessionView(APIView):
    def get(self, request, username):
        try:
            # 🌟 Find the ServiceProfile using the explicit username parameter
            service_prof = ServiceProfile.objects.filter(profile__profile__username=username).first()

            if not service_prof:
                return Response({"devices": []}, status=status.HTTP_200_OK)

            devices_data = []
            for conn in service_prof.connections.all():
                devices_data.append({
                    "device_id": conn.device_id,
                    "model_name": conn.model_name,
                    "is_blocked": conn.is_blocked,
                    "traffic_used": conn.traffic_used
                })
            return Response({"devices": devices_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ToggleBlockDeviceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        device_id = request.data.get("device_id")
        if not device_id:
            return Response({"error": "Device ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            connection = Connection.objects.get(device_id=device_id)
            # Toggle the block state
            connection.is_blocked = not connection.is_blocked
            connection.save()

            return Response({
                "message": "وضعیت دستگاه با موفقیت تغییر کرد",
                "is_blocked": connection.is_blocked
            }, status=status.HTTP_200_OK)
        except Connection.DoesNotExist:
            return Response({"error": "دستگاه یافت نشد"}, status=status.HTTP_404_NOT_FOUND)


class UpdateDeviceUsageView(APIView):
    # 🌟 CRITICAL: Must be exact lowercase 'post'
    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        device_id = request.data.get("device_id")
        bytes_used = request.data.get("bytes_used", 0)

        if not username or not device_id:
            return Response({"error": "نام کاربری و شناسه دستگاه الزامی هستند"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            service_prof = ServiceProfile.objects.filter(profile__profile__username=username).first()
            if not service_prof:
                return Response({"error": "پروفایل کاربری یافت نشد"}, status=status.HTTP_404_NOT_FOUND)

            connection = service_prof.connections.filter(device_id=device_id).first()
            if not connection:
                return Response({"error": "دستگاه به این حساب متصل نیست"}, status=status.HTTP_404_NOT_FOUND)

            connection.traffic_used += int(bytes_used)
            connection.save()

            return Response({"message": "مصرف دستگاه با موفقیت بروزرسانی شد"}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
