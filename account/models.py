from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class UserProfile(models.Model):
    profile = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.IntegerField(unique=True)
    nationalCode = models.IntegerField(null=True, blank=True)

    def __str__(self):

        return str(self.phone_number)

