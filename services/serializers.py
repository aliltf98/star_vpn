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

    class Meta:  # اصلاح شده از File به Meta
        model = UriCode
        fields = ['id', 'value', 'category_name', 'remainingVolume']
