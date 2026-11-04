import logging
import requests
from django.conf import settings
from services.currency import convert_toman_to_usd

logger = logging.getLogger(__name__)

OXAPAY_CREATE_INVOICE_URL = "https://api.oxapay.com/v1/payment/invoice"

def create_oxapay_invoice(order_id: str, toman_amount: float, description: str = "") -> dict | None:
    """
    دریافت قیمت تومانی محصول از market، تبدیل به دلار بر اساس نرخ TGJU/RiskBuffer
    و ارسال درخواست ساخت فاکتور به API OxaPay
    """
    # تبدیل مبلغ تومانی به دلار
    usd_amount = convert_toman_to_usd(toman_amount)

    payload = {
        "amount": usd_amount,
        "currency": "USD",
        "order_id": str(order_id),
        "lifetime": 30,  # مهلت ۳۰ دقیقه برای پرداخت
        "fee_paid_by_payer": 1,  # پرداخت کارمزد توسط خریدار
        "under_paid_coverage": 2.5,
        "return_url": settings.OXAPAY_RETURN_URL,
        "callback_url": settings.OXAPAY_CALLBACK_URL,
        "description": description or f"StarVPN Order #{order_id}",
    }

    headers = {
        "merchant_api_key": settings.OXAPAY_MERCHANT_KEY,
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(OXAPAY_CREATE_INVOICE_URL, json=payload, headers=headers, timeout=10)
        data = response.json()

        if response.status_code == 200 and data.get("result") == 100:
            logger.info(f"OxaPay Invoice created for Order #{order_id} - {usd_amount} USD")
            return {
                "track_id": data.get("track_id"),
                "pay_url": data.get("pay_url"),
                "usd_amount": usd_amount,
            }
        else:
            logger.error(f"OxaPay API Error: {data.get('message')}")
            return None

    except Exception as e:
        logger.error(f"OxaPay Exception: {e}")
        return None