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
        try:
            serializer = SigninSerializer(data=request.data)
            print(serializer)
            if serializer.is_valid():
                username = serializer.data.get('username')
                password = serializer.data.get('password')
                user = None
                print(username)
                if UserProfile.objects.filter(profile__username=username).exists():
                    user = authenticate(request, username=username, password=password)
                elif UserProfile.objects.filter(phone_number=username).exists():
                    usr = UserProfile.objects.get(phone_number=username)
                    user = authenticate(request, username=usr.profile.username, password=password)
                if user is None:
                    return Response({'status': serializer.errors ,"message": "حساب کاربری یا کلمه عبور اشتباه است"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    token, created = Token.objects.get_or_create(user=user)
                    return Response({
                        'token': token.key,
                        'message': "ورود با موفقیت انجام شد"
                    }, status=status.HTTP_200_OK)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return Response({
                'error': "except",
                'message': e
            }, status=status.HTTP_200_OK)

