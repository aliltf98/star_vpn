from django.urls import path
from .views import *

urlpatterns = [
    path("register", register, name="register"),
    path('logout', signout, name="logout"),
    path('account/subscription/<username>', subscription, name="subs"),
]
