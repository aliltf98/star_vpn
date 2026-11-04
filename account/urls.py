from django.urls import path
from .views import *

urlpatterns = [
    path("register", register, name="register"),
    path('logout', signout, name="logout"),
    path('account/subscription/', subscription, name="subs"),
    path('dashboard', dashboard_view),
    path('dashboard/profile', profile_view, name="profile"),
]
