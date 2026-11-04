from django.contrib import admin
from django.contrib import messages
from .models import Order, MarketerProfile, Commission, PayoutRequest, UserSubscription
from .services import PaymentProcessingService


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'plan', 'final_amount', 'gateway_name', 'status', 'ref_id', 'created_at')
    list_filter = ('status', 'gateway_name', 'created_at')
    search_fields = ('user__username', 'ref_id', 'id')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['approve_and_activate_orders', 'reject_orders']

    @admin.action(description="تایید سفارش و شارژ خودکار در مرزبان")
    def approve_and_activate_orders(self, request, queryset):
        success_count = 0
        for order in queryset:
            if order.status != Order.StatusChoices.COMPLETED:
                try:
                    PaymentProcessingService.process_successful_order(order, ref_id=order.ref_id or "MANUAL_CONFIRMED")
                    success_count += 1
                except Exception as e:
                    self.message_user(request, f"خطا در فعال‌سازی سفارش #{order.id}: {str(e)}", level=messages.ERROR)

        if success_count > 0:
            self.message_user(request, f"تعداد {success_count} سفارش با موفقیت در مرزبان فعال گردید.")

    @admin.action(description="رد سفارش‌های انتخابی")
    def reject_orders(self, request, queryset):
        updated = queryset.update(status=Order.StatusChoices.FAILED)
        self.message_user(request, f"تعداد {updated} سفارش رد شد.")


@admin.register(MarketerProfile)
class MarketerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'wallet_balance', 'first_order_commission_rate', 'renewal_commission_rate', 'is_active')
    search_fields = ('user__username', 'code')


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ('marketer', 'order', 'commission_type', 'commission_amount', 'status', 'created_at')


@admin.register(PayoutRequest)
class PayoutRequestAdmin(admin.ModelAdmin):
    list_display = ('marketer', 'amount', 'shaba_number', 'status', 'created_at')


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'expire_date', 'total_volume_gb', 'is_active')