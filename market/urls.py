from django.urls import path
from . import views

urlpatterns = [
    path('checkout/<int:plan_id>/', views.checkout_view, name='checkout'),
    path('process-checkout/', views.process_checkout, name='process_checkout'),
    # path('manual-payment/<uuid:order_id>/', views.manual_payment_view, name='manual_payment'),
    path('initiate-payment/<int:plan_id>/', views.initiate_payment, name='initiate_payment'),
    path('callback/', views.payment_callback, name='payment_callback'),
    path('validate-referral/', views.validate_referral_code, name='validate_referral'),
]