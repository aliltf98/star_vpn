from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import *


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
    new_password = serializers.CharField(required=True, write_only=True)
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

        # اعمال اعتبارسنج‌های امنیتی تعریف‌شده در settings.py
        validate_password(data['new_password'], self.context['request'].user)
        return data
