# account/models.py
from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    profile = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True) # بهینه‌سازی
    referred_by = models.ForeignKey(
        'market.MarketerProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referred_users'
    )

    def __str__(self):
        return str(self.phone_number)