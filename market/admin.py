from django.contrib import admin
from .models import MarketerProfile, Order, Commission, PayoutRequest


@admin.register(MarketerProfile)
class MarketerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'first_order_commission_rate', 'renewal_commission_rate', 'discount_rate', 'wallet_balance', 'is_active')
    search_fields = ('code', 'user__username', 'user__email')
    list_filter = ('is_active',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'plan', 'plan_price', 'final_amount', 'is_first_order', 'status', 'created_at')
    list_filter = ('status', 'is_first_order', 'created_at')
    search_fields = ('id', 'user__username', 'authority', 'ref_id')


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ('marketer', 'order', 'commission_type', 'commission_amount', 'applied_rate', 'status', 'created_at')
    list_filter = ('commission_type', 'status', 'created_at')
    search_fields = ('marketer__code', 'order__id')


@admin.register(PayoutRequest)
class PayoutRequestAdmin(admin.ModelAdmin):
    list_display = ('marketer', 'amount', 'shaba_number', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('marketer__code', 'shaba_number')