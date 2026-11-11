# account/models.py
from django.contrib.auth.models import User
from django.db import models

from django.utils.translation import gettext_lazy as _


class UserProfile(models.Model):
    class UserType(models.TextChoices):
        ADMIN = 'admin', _('admin user')
        SELLER = 'seller', _('seller user')
        REGULAR = 'regular', _('regular user')

    profile = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    type = models.CharField(choices=UserType.choices, default=UserType.REGULAR, max_length=10, verbose_name="user type")

    # ارتباط مستقیم با پروفایل مارکتر (که همان سیستم معرفی/Promo Code است)
    referred_by = models.ForeignKey(
        'market.MarketerProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referred_users',
        verbose_name="مارکتر معرفی‌کننده"
    )

    def __str__(self):
        return str(self.phone_number or self.profile.username)