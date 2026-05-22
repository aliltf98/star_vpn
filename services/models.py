from django.contrib.auth.models import User
from django.db import models

from account.models import UserProfile


class ConnectionsLog(models.Model):
    value = models.TextField()

class Connection(models.Model):
    device_id = models.CharField(max_length=255) # همان ANDROID_ID یا UUID
    model_name = models.CharField(max_length=255) # مثال: Samsung SM-G991B
    last_login = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.model_name} ({self.device_id})"

class Category(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class UriCode(models.Model):
    value = models.CharField(max_length=999)
    type = models.ForeignKey(Category, on_delete=models.CASCADE)
    volume = models.FloatField()
    remainingVolume = models.FloatField()

    def __str__(self):
        return self.value

class ServiceProfile(models.Model):
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    configs = models.ManyToManyField(UriCode)
    connections = models.ManyToManyField(Connection)
    Logs = models.ManyToManyField(ConnectionsLog)

    def __str__(self):
        return self.profile.profile.username
