from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from market.services import OrderService, PaymentProcessingService
from market.models import Order


@login_required
def initiate_payment(request, plan_id):
    # پذیرش هر دو متد POST و GET (جهت پشتیبانی از ارجاع بعد از لاگین)
    order, error = OrderService.create_order(request.user, plan_id)

    if error:
        return redirect('home')

    # متصل کردن به درگاه یا شبیه‌ساز پرداخت
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
        # تایید پرداخت و فعال‌سازی
        PaymentProcessingService.process_successful_order(order, ref_id="123456789")
        return render(request, 'payment_result.html', {'success': True, 'order': order})

    order.status = Order.StatusChoices.FAILED
    order.save()
    return render(request, 'payment_result.html',
                  {'success': False, 'error': 'پرداخت توسط کاربر لغو شد یا ناموفق بود.'})