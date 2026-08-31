from django.urls import path
from . import views

urlpatterns = [
    path('checkout/<int:plan_id>/', views.initiate_payment, name='initiate_payment'),
    path('callback/', views.payment_callback, name='payment_callback'),
]