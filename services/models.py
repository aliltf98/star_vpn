from django.contrib.auth.models import User
from django.db import models

from account.models import UserProfile


class ConnectionsLog(models.Model):
    value = models.TextField()

class Connection(models.Model):
    value = models.TextField()

class Category(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title

class UriCode(models.Model):
    value = models.CharField(max_length=999)
    type = models.ForeignKey(Category, on_delete=models.CASCADE)
    def __str__(self):
        return self.value

class ServiceProfile(models.Model):
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    configs = models.ManyToManyField(UriCode)
    connections = models.ManyToManyField(Connection)
    Logs = models.ManyToManyField(ConnectionsLog)

    def __str__(self):
        return self.profile.profile.username
