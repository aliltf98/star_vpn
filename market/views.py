import math
import time
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from market.services import OrderService, PaymentProcessingService
from .models import Order, MarketerProfile
from main.models import MainPlansLayout
from services.PanelManager import PanelManager
from services.currency import get_live_usdt_rate, convert_toman_to_usd


@login_required
def checkout_view(request, plan_id):
    plan = get_object_or_404(MainPlansLayout, id=plan_id)
    username = request.user.username

    # ۱. استعلام وضعیت فعلی کاربر از مرزبان
    user_info = PanelManager.get_user_info(username)

    current_data_gb = 0
    current_expire_timestamp = 0
    current_remaining_days = 0
    now_timestamp = int(time.time())

    if user_info and isinstance(user_info, dict):
        used_bytes = user_info.get('used_traffic', 0) or 0
        limit_bytes = user_info.get('data_limit', 0) or 0
        remaining_bytes = max(0, limit_bytes - used_bytes)
        current_data_gb = round(remaining_bytes / (1024 ** 3), 2)

        current_expire_timestamp = user_info.get('expire') or 0
        if current_expire_timestamp > now_timestamp:
            remaining_seconds = current_expire_timestamp - now_timestamp
            current_remaining_days = math.ceil(remaining_seconds / 86400)

    # ۲. محاسبات مجموع حجم و زمان جدید
    final_data_gb = round(current_data_gb + plan.volume_gb, 2)
    added_days = plan.duration_days
    final_days = current_remaining_days + added_days
    base_timestamp = max(now_timestamp, current_expire_timestamp)
    final_expire_timestamp = base_timestamp + (added_days * 86400)

    # ۳. محاسبات مالی
    usdt_rate = get_live_usdt_rate()
    usd_price = convert_toman_to_usd(plan.price)

    context = {
        'plan': plan,
        'current_data_gb': current_data_gb,
        'added_data_gb': plan.volume_gb,
        'final_data_gb': final_data_gb,
        'current_remaining_days': current_remaining_days,
        'added_days': added_days,
        'final_days': final_days,
        'final_expire_timestamp': final_expire_timestamp,
        'toman_price': plan.price,
        'usd_price': usd_price,
        'usdt_rate': usdt_rate,
        'is_existing_user': bool(user_info),
    }

    return render(request, 'checkout.html', context)


@login_required
def process_checkout(request):
    """پردازش ثبت اولیه سفارش از صفحه پیش‌فاکتور"""
    if request.method == "POST":
        plan_id = request.POST.get('plan_id')
        payment_method = request.POST.get('payment_method', 'oxapay')

        order, error = OrderService.create_order(request.user, plan_id, gateway_name=payment_method)
        if error:
            messages.error(request, error)
            return redirect('home')

        if payment_method == 'oxapay':
            # هدایت به درگاه اتوماتیک اکساپِی (منطق موجود پروژه)
            # return redirect('oxapay_payment_url', order_id=order.id)
            pass
        elif payment_method == 'zarinpal':
            return redirect('initiate_payment', plan_id=plan_id)

    return redirect('home')


@login_required
def initiate_payment(request, plan_id):
    order, error = OrderService.create_order(request.user, plan_id, gateway_name='zarinpal')

    if error:
        return redirect('home')

    sample_authority = f"AUTH_{order.id.hex[:10]}"
    order.authority = sample_authority
    order.save()

    return redirect(f"/fa/callback/?Authority={sample_authority}&Status=OK")


def payment_callback(request):
    authority = request.GET.get('Authority')
    status = request.GET.get('Status')

    if not authority:
        return render(request, 'payment_result.html', {'success': False, 'error': 'کد شناسه پرداخت یافت نشد.'})

    try:
        order = Order.objects.get(authority=authority, status=Order.StatusChoices.PENDING)
    except Order.DoesNotExist:
        return render(request, 'payment_result.html',
                      {'success': False, 'error': 'سفارش معتبری در انتظار پرداخت یافت نشد.'})

    if status == 'OK':
        PaymentProcessingService.process_successful_order(order, ref_id="123456789")
        return render(request, 'payment_result.html', {'success': True, 'order': order})

    order.status = Order.StatusChoices.FAILED
    order.save()
    return render(request, 'payment_result.html',
                  {'success': False, 'error': 'پرداخت توسط کاربر لغو شد یا ناموفق بود.'})


@login_required
def validate_referral_code(request):
    if request.method == "POST":
        code = request.POST.get('code', '').strip()
        if not code:
            return JsonResponse({'valid': False, 'message': 'کد معرف وارد نشده است.'})

        try:
            marketer = MarketerProfile.objects.get(code=code)
            return JsonResponse({
                'valid': True,
                'message': f'کد معرف معتبر است (معرف: {marketer.user.username})'
            })
        except MarketerProfile.DoesNotExist:
            return JsonResponse({'valid': False, 'message': 'کد معرف یافت نشد.'})

    return JsonResponse({'valid': False, 'message': 'درخواست نامعتبر است.'})