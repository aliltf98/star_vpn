# account/models.py
from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    profile = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.BigIntegerField(unique=True)  # تغییر به BigIntegerField برای جلوگیری از Overflow شماره موبایل

    # اتصال دائمی کاربر به نماینده/بازاریاب
    referred_by = models.ForeignKey(
        'market.MarketerProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referred_users'
    )

    def __str__(self):
        return str(self.phone_number)