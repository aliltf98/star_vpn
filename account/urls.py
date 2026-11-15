from django.urls import path
from .views import *

urlpatterns = [
    path("register", register, name="register"),
    path('logout', signout, name="logout"),
    path('account/subscription/', subscription, name="subs"),
    path('dashboard', dashboard_view, name='dashboard'),
    path('dashboard/profile', profile_view, name="profile"),
    path('dashboard/new_user', new_user, name="new_user"),
    path('dashboard/wallet', dashboard_wallet, name='dashboard_wallet'),
    path('dashboard/subscription/', dashboard_subscription, name='dashboard_subscription'),
    path('dashboard/services/new/', new_service_order, name='new_service_order'),
    path('dashboard/services/order/<int:plan_id>/', select_plan_order, name='select_plan_order'),
]
