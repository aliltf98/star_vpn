# panelmanager.py
from curl_cffi import requests

BASE_URL = "https://mediadownload.eu.org/api"
ADMIN_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJyZXphIiwiYWNjZXNzIjoiYWRtaW4iLCJpYXQiOjE3NzY4NTExMjR9.90CzZtHSdb8I7PJUNs-nE7hrD1YRQ_b311zSCWY1lBA"
headers = {
    "Authorization": f"Bearer {ADMIN_TOKEN}",
    "Content-Type": "application/json"
}
PROXIES = {
    'http': 'http://m0kvE6Vpqz22:K0oRxaoNfz22@127.0.0.1:110',
    'https': 'http://m0kvE6Vpqz22:K0oRxaoNfz22@127.0.0.1:110',
}

class PanelManager:


    @classmethod
    def get_headers(cls):
        return {
            "Authorization": f"Bearer {cls.ADMIN_TOKEN}",
            "Content-Type": "application/json"
        }

    @classmethod
    def create_user(cls, username, data_limit_gb=10):
        """ساخت کاربر جدید در پنل"""
        url = f"{cls.BASE_URL}/user"
        payload = {
            "username": username,
            "data_limit": data_limit_gb * 1024 * 1024 * 1024,
            "status": "active",
            "proxies": {"vless": {}, "vmess": {}, "trojan": {}},
            "inbounds": {
                "vless": ["VLESS TCP REALITY", "VLESS GRPC REALITY"],
                "vmess": ["VMess TCP", "VMess Websocket"]
            }
        }
        response = requests.post(
            url,
            json=payload,
            headers=cls.get_headers(),
            proxies=cls.PROXIES,
            timeout=10
        )
        return response.json() if response.status_code == 200 else None

    @staticmethod
    def get_user_info(username):
        url = f"{BASE_URL}/user/{username}"

        # 🎯 تعریف یک Session برای زنده نگه داشتن و مدیریت درست تونل TLS
        session = requests.Session()
        session.proxies = PROXIES

        # 🎯 اضافه کردن هدرهای کاملاً طبیعی مرورگر برای فریب دادن فیلترینگ/دیوار آتش
        headers = {
            "Authorization": f"Bearer {ADMIN_TOKEN}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive"
        }

        try:
            print(f"🔄 ارسال درخواست امن به پنل برای: {username}")

            # ارسال درخواست از طریق Session با تنظیم هدرها و تایم‌اوت بالا
            response = session.get(url, headers=headers, timeout=15)

            print(f"📥 پاسخ دریافت شد. کد وضعیت: {response.status_code}")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"⚠️ پاسخ ناوفق پنل: {response.text}")
                return None

        except Exception as e:
            print(f"❌ خطا در لایه ارتباطی پایتون: {str(e)}")
            return None

    @staticmethod
    def get_user_usage(username):
        url = f"{BASE_URL}/user/{username}/usage"

        headers = {
            "Authorization": f"Bearer {ADMIN_TOKEN}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json"
        }

        try:
            print(f"📊 در حال دریافت میزان مصرف کاربر: {username} از پنل...")

            # استفاده از curl_cffi برای جعل اثر انگشت TLS مرورگر کروم
            response = requests.get(
                url,
                headers=headers,
                proxies=PROXIES,
                timeout=12,
                impersonate="chrome"  # 🎯 شبیه‌سازی کامل مرورگر کروم
            )

            if response.status_code == 200:
                return response.json()
            else:
                print(f"⚠️ پنل متصل شد اما کد وضعیت دریافت مصرف {response.status_code} بود.")
                return None

        except Exception as e:
            print(f"❌ خطا در دریافت میزان مصرف کاربر {username}: {str(e)}")
            return None
