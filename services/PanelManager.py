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
        headers = {
            "Authorization": f"Bearer {ADMIN_TOKEN}"
        }
        try:
            print(f"🔄 ارسال درخواست مجهز به اثر انگشت مرورگر برای کاربر: {username}")

            # 🎯 راز اصلی: اضافه کردن impersonate="chrome" برای عبور از سد فیلترینگ و CDN
            response = requests.get(
                url,
                headers=headers,
                proxies=PROXIES,
                timeout=15,
                impersonate="chrome"
            )

            print(f"📥 پاسخ پنل دریافت شد. کد وضعیت: {response.status_code}")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"⚠️ پاسخ ناموفق از پنل با کد: {response.status_code}")
                return None

        except Exception as e:
            print(f"❌ خطا در ارتباط امن با پنل: {str(e)}")
            return None

    @staticmethod
    def get_user_usage(username):
        url = f"{BASE_URL}/user/{username}/usage"
        headers = {
            "Authorization": f"Bearer {ADMIN_TOKEN}"
        }
        try:
            print(f"📊 دریافت میزان مصرف کاربر: {username}")
            response = requests.get(
                url,
                headers=headers,
                proxies=PROXIES,
                timeout=15,
                impersonate="chrome"
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"❌ خطا در دریافت مصرف: {str(e)}")
        return None
