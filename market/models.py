import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from main.models import MainPlansLayout


class MarketerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='marketer_profile', verbose_name=_('User'))
    code = models.CharField(max_length=50, unique=True, verbose_name=_('Referral / Promo Code'))

    first_order_commission_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=30.00, verbose_name=_('First Order Commission Rate (%)')
    )
    renewal_commission_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=10.00, verbose_name=_('Renewal Commission Rate (%)')
    )
    discount_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=10.00, verbose_name=_('Customer Discount Rate (%)')
    )

    wallet_balance = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name=_('Wallet Balance'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))

    class Meta:
        verbose_name = _('Marketer Profile')
        verbose_name_plural = _('Marketer Profiles')

    def __str__(self):
        return f"{self.user.username} ({self.code})"


class Order(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = 'pending', _('Pending')
        COMPLETED = 'completed', _('Completed')
        FAILED = 'failed', _('Failed')
        CANCELED = 'canceled', _('Canceled')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name=_('User'))
    plan = models.ForeignKey(MainPlansLayout, on_delete=models.SET_NULL, null=True, verbose_name=_('Plan'))

    plan_price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name=_('Plan Price'))
    discount_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name=_('Discount Amount'))
    final_amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name=_('Final Amount'))

    is_first_order = models.BooleanField(default=False, verbose_name=_('Is First Order'))
    status = models.CharField(max_length=10, choices=StatusChoices.choices, default=StatusChoices.PENDING,
                              verbose_name=_('Status'))

    authority = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Authority'))
    ref_id = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Reference ID'))
    gateway_name = models.CharField(max_length=50, default='zarinpal', verbose_name=_('Gateway Name'))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    def __str__(self):
        return f"Order {self.id} - {self.user.username} ({self.get_status_display()})"


class Commission(models.Model):
    class CommissionTypes(models.TextChoices):
        FIRST_ORDER = 'first_order', _('First Order')
        RENEWAL = 'renewal', _('Renewal')

    class StatusChoices(models.TextChoices):
        PENDING = 'pending', _('Pending')
        APPROVED = 'approved', _('Approved')
        REJECTED = 'rejected', _('Rejected')

    marketer = models.ForeignKey(MarketerProfile, on_delete=models.CASCADE, related_name='commissions',
                                 verbose_name=_('Marketer'))
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='commission', verbose_name=_('Order'))
    commission_type = models.CharField(max_length=20, choices=CommissionTypes.choices,
                                       verbose_name=_('Commission Type'))

    order_amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name=_('Order Amount'))
    commission_amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name=_('Commission Amount'))
    applied_rate = models.DecimalField(max_digits=5, decimal_places=2, verbose_name=_('Applied Rate (%)'))

    status = models.CharField(max_length=10, choices=StatusChoices.choices, default=StatusChoices.APPROVED,
                              verbose_name=_('Status'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))

    class Meta:
        verbose_name = _('Commission')
        verbose_name_plural = _('Commissions')

    def __str__(self):
        return f"{self.marketer.code} - {self.commission_amount}"


class PayoutRequest(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = 'pending', _('Pending')
        PAID = 'paid', _('Paid')
        REJECTED = 'rejected', _('Rejected')

    marketer = models.ForeignKey(MarketerProfile, on_delete=models.CASCADE, related_name='payouts',
                                 verbose_name=_('Marketer'))
    amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name=_('Amount'))
    shaba_number = models.CharField(max_length=30, verbose_name=_('SHEBA Number'))
    status = models.CharField(max_length=10, choices=StatusChoices.choices, default=StatusChoices.PENDING,
                              verbose_name=_('Status'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))

    class Meta:
        verbose_name = _('Payout Request')
        verbose_name_plural = _('Payout Requests')

    def __str__(self):
        return f"Payout {self.amount} - {self.marketer.user.username}"


class UserSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions', verbose_name=_('User'))
    plan = models.ForeignKey(MainPlansLayout, on_delete=models.SET_NULL, null=True, verbose_name=_('Plan'))
    order = models.OneToOneField(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='subscription',
                                 verbose_name=_('Order'))

    start_date = models.DateTimeField(auto_now_add=True, verbose_name=_('Start Date'))
    expire_date = models.DateTimeField(verbose_name=_('Expire Date'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))

    # پیشنهاد: افزودن میزان مصرف و محدودیت برای لینک به مرزبان/3X-UI
    total_volume_gb = models.PositiveIntegerField(default=0)
    used_volume_bytes = models.BigIntegerField(default=0)
    subscription_url = models.URLField(max_length=500, blank=True, null=True)  # لینک سابسکرایپشن کاربر