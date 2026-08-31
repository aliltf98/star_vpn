from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .services import *

def payment_callback(request):
    authority = request.GET.get('Authority')
    status = request.GET.get('Status')

    try:
        order = Order.objects.get(authority=authority, status=Order.StatusChoices.PENDING)
    except Order.DoesNotExist:
        return render(request, 'payment_result.html', {'error': 'سفارش یافت نشد.'})

    if status == 'OK':
        # استعلام از درگاه (ZarinPal Verify)
        # is_valid, ref_id = ZarinpalGateway.verify(authority, order.final_amount)
        is_valid = True
        ref_id = "123456789" # کد پیگیری نمونه دریافتی از بانک

        if is_valid:
            # فراخوانی سرویس فعال‌سازی
            PaymentProcessingService.process_successful_order(order, ref_id)
            return render(request, 'payment_result.html', {'success': True, 'order': order})

    # در صورت لغو یا خطا در پرداخت
    order.status = Order.StatusChoices.FAILED
    order.save()
    return render(request, 'payment_result.html', {'success': False, 'error': 'پرداخت ناموفق بود.'})


@login_required
def initiate_payment(request, plan_id):
    if request.method == 'POST':
        promo_code = request.POST.get('promo_code', '').strip()

        order, error = OrderService.create_order(request.user, plan_id, promo_code)
        if error:
            # نمایش خطا در صورت نبود پلن
            return redirect('home')

        # اتصال به API درگاه (مثلاً زرین‌پال)
        # authority, payment_url = ZarinpalGateway.request_payment(order.final_amount, order.id)

        # کد نمونه فرضی برای تست:
        order.authority = "SAMPLE_AUTHORITY_123"
        order.save()

        # هدایت کاربر به صفحه درگاه
        # return redirect(payment_url)
        return redirect('payment_callback')  # برای تست به کال‌بک هدایت می‌کنیم

    return redirect('home')