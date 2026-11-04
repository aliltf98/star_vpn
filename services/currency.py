import logging
from decimal import Decimal

import requests
from django.core.cache import cache

logger = logging.getLogger(__name__)

CACHE_KEY_USDT_RATE = "live_usdt_toman_rate"
CACHE_TIMEOUT = 300  # 5 دقیقه
DEFAULT_RISK_BUFFER_PERCENT = 2.0  # 2% حاشیه اطمینان

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
}


def fetch_tgju_usd_rate() -> float | None:
    """دریافت نرخ دلار بازار آزاد مستقیماً از وب‌سرویس TGJU"""
    url = "https://call2.tgju.org/ajax.json"
    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # قیمت دلار آزاد در کلیات پاسخ TGJU
            price_info = data.get("current", {}).get("price_dollar_rl")
            if price_info and "p" in price_info:
                # مقدار ریالی به صورت رشته با کاما (مثلاً "650,000") ارسال می‌شود
                raw_price = price_info["p"].replace(",", "")
                toman_price = float(raw_price) / 10  # تبدیل ریال به تومان
                return toman_price
    except Exception as e:
        logger.warning(f"TGJU Fetch Error: {e}")
    return None


def fetch_nobitex_usdt_rate() -> float | None:
    """دریافت نرخ تتر از نوبیتکس (پشتیبان اول)"""
    url = "https://api.nobitex.ir/v2/orderbook/USDTIRT"
    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok" and "bids" in data and len(data["bids"]) > 0:
                return float(data["bids"][0][0]) / 10
    except Exception as e:
        logger.warning(f"Nobitex Fetch Error: {e}")
    return None


def get_live_usdt_rate(risk_buffer_percent: float = DEFAULT_RISK_BUFFER_PERCENT) -> float:
    """دریافت نرخ نهایی دلار/تتر بر اساس TGJU + پشتیبان نوبیتکس + Cache"""
    base_rate = None

    # 1. بررسی Cache در ابتدا
    try:
        base_rate = cache.get(CACHE_KEY_USDT_RATE)
    except Exception:
        base_rate = None

    # 2. استعلام از TGJU در صورت عدم وجود در کش
    if not base_rate:
        base_rate = fetch_tgju_usd_rate()

        # 3. سوئیچ به نوبیتکس در صورت قطع بودن TGJU
        if not base_rate:
            logger.info("TGJU unavailable, switching to Nobitex...")
            base_rate = fetch_nobitex_usdt_rate()

        # 4. ذخیره نرخ جدید در Cache
        if base_rate:
            try:
                cache.set(CACHE_KEY_USDT_RATE, base_rate, timeout=CACHE_TIMEOUT)
                cache.set(f"{CACHE_KEY_USDT_RATE}_backup", base_rate, timeout=86400 * 7)
            except Exception as e:
                logger.error(f"Cache Set Error: {e}")
        else:
            # 5. استفاده از پشتیبان اضطراری کش قدیمی
            try:
                base_rate = cache.get(f"{CACHE_KEY_USDT_RATE}_backup")
            except Exception:
                base_rate = None

            if not base_rate:
                base_rate = 90000.0  # نرخ اضطراری فرضی
                logger.critical("All sources failed. Using hardcoded emergency rate.")

    # اعمال حاشیه اطمینان (Risk Buffer)
    final_rate = base_rate * (1 + (risk_buffer_percent / 100.0))
    return round(final_rate, 2)


def convert_toman_to_usd(toman_amount: float | Decimal,
                         risk_buffer_percent: float = DEFAULT_RISK_BUFFER_PERCENT) -> float:
    """تبدیل قیمت بسته تومانی به معادل دلاری جهت ارسال به OxaPay"""
    usdt_rate = get_live_usdt_rate(risk_buffer_percent=risk_buffer_percent)

    # تبدیل متغیر تومان به float در صورت Decimal بودن فیلد دیتابیس
    toman_float = float(toman_amount)

    usd_amount = toman_float / usdt_rate
    return round(usd_amount, 2)