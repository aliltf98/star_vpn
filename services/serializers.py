from rest_framework import serializers
from .models import *


class SignupSerializer(serializers.Serializer):
    number = serializers.CharField(max_length=14)
    username = serializers.CharField(max_length=60)
    password = serializers.CharField(max_length=60)

class SigninSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=60, required=True, allow_null=False, allow_blank=False)
    password = serializers.CharField(max_length=60, required=True, allow_null=False, allow_blank=False)

class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = ServiceProfile
        fields = ['profile', 'configs', 'connections', 'Logs']
