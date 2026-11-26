from .models import *

from django.contrib.auth.models import User
from rest_framework import serializers
from account.models import UserProfile
from main.models import MainPlansLayout
from market.models import MarketerProfile


class AppSignupSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=60, required=True)
    password = serializers.CharField(max_length=60, required=True, write_only=True)
    phone_number = serializers.CharField(max_length=15, required=False, allow_blank=True, allow_null=True)
    plan_id = serializers.IntegerField(required=True)
    referral_code = serializers.CharField(max_length=50, required=False, allow_blank=True, allow_null=True)
    device_id = serializers.CharField(max_length=255, required=True)
    model_name = serializers.CharField(max_length=255, required=False, default="Unknown")

    def validate_username(self, value):
        value = value.strip()
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("این نام کاربری قبلاً در سیستم ثبت شده است.")
        return value

    def validate_phone_number(self, value):
        if value:
            value = value.strip()
            if UserProfile.objects.filter(phone_number=value).exists():
                raise serializers.ValidationError("این شماره همراه قبلاً ثبت شده است.")
        return value or None

    def validate_plan_id(self, value):
        if not MainPlansLayout.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError("پلن انتخاب‌شده معتبر نیست یا غیرفعال است.")
        return value

    def validate_referral_code(self, value):
        if value:
            value = value.strip()
            if not MarketerProfile.objects.filter(code=value, is_active=True).exists():
                raise serializers.ValidationError("کد معرف وارد شده معتبر نیست.")
        return value or None

class SignupSerializer(serializers.Serializer):
    number = serializers.CharField(max_length=14)
    username = serializers.CharField(max_length=60)
    password = serializers.CharField(max_length=60)


class SigninSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=60, required=True, allow_null=False, allow_blank=False)
    password = serializers.CharField(max_length=60, required=True, allow_null=False, allow_blank=False)


class UriCodeSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='type.title', read_only=True)

    class Meta:
        model = UriCode
        fields = ['id', 'value', 'category_name', 'remainingVolume']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, min_length=4)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("رمز عبور فعلی اشتباه است.")
        return value

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "رمز عبور جدید و تکرار آن یکسان نیستند."})

        if data['old_password'] == data['new_password']:
            raise serializers.ValidationError({"new_password": "رمز عبور جدید نباید با رمز فعلی یکسان باشد."})

        return data