from django.contrib.auth.models import User
from django.db import models
from account.models import UserProfile
from market.models import UserSubscription


class ConnectionsLog(models.Model):
    value = models.TextField()

class Category(models.Model):
    title = models.CharField(max_length=100)
    protocol = models.CharField(max_length=20, default='vless')  # vless, vmess, trojan

    def __str__(self):
        return self.title


class UriCode(models.Model):
    subscription = models.ForeignKey(UserSubscription, on_delete=models.CASCADE, related_name='configs', null=True,
                                     blank=True)
    value = models.TextField(verbose_name="Config URI")
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category.title} - {self.id}"




class ServiceProfile(models.Model):
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    configs = models.ManyToManyField(UriCode, blank=True)
    Logs = models.ManyToManyField(ConnectionsLog, blank=True)

    def __str__(self):
        return self.profile.profile.username

class Connection(models.Model):
    service_profile = models.ForeignKey(
        ServiceProfile,
        on_delete=models.CASCADE,
        related_name='connections',
        null=True,
        blank=True
    )
    subscription = models.ForeignKey(UserSubscription, on_delete=models.CASCADE, related_name='connections', null=True, blank=True)
    device_id = models.CharField(max_length=255)
    model_name = models.CharField(max_length=255)
    is_blocked = models.BooleanField(default=False)
    traffic_used = models.BigIntegerField(default=0)
    last_login = models.DateTimeField(auto_now=True)

    class Meta:
        # هر دستگاه برای هر پروفایل سرویس فقط یک رکورد یکتا دارد
        unique_together = ('service_profile', 'device_id')

    def __str__(self):
        return f"{self.model_name} ({self.device_id})"