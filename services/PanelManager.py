# panelmanager.py
import requests


class PanelManager:
    # 🎯 بازگشت به دامنه اصلی (کلودفلر ترافیک تمیز هدر را عبور می‌دهد)
    BASE_URL = "https://mediadownload.eu.org/api"

    # 🔑 توکن جدید، زنده و تایید شده شما از لاگ بالا
    ADMIN_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbWlyIiwiYWNjZXNzIjoiYWRtaW4iLCJpYXQiOjE3ODMwOTAzMTZ9.1kk4Nr3YyYrVBOMmJMrqdIW_ElzM_18AUOTQwbujC8E"

    @classmethod
    def get_headers(cls):
        """ساخت هدرهای کاملاً منطبق بر مرورگر برای عبور از فایروال"""
        return {
            "Authorization": f"Bearer {cls.ADMIN_TOKEN}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            # شبیه‌سازی فینگرپرینت مروگر برای جلوگیری از خطای دیسکانکت اس‌اس‌ال
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive"
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
        try:
            print(f" [+] Requesting Panel via Domain to create: {username}", flush=True)
            # حذف پارامتر پروکسی برای اتصال مستقیم و امن HTTPS
            response = requests.post(url, json=payload, headers=cls.get_headers(), timeout=15)
            print(f" [-] Panel Response: {response.status_code}", flush=True)
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f" [!] Connection Error in create_user: {str(e)}", flush=True)
            return None

    @classmethod
    def get_user_info(cls, username):
        """دریافت اطلاعات کاربر"""
        url = f"{cls.BASE_URL}/user/{username}"
        try:
            print(f" [🚀] Requesting Panel via Domain for info: {username}", flush=True)
            response = requests.get(url, headers=cls.get_headers(), timeout=15)
            print(f" [📥] Panel Response: {response.status_code}", flush=True)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f" [!] Connection Error in get_user_info: {str(e)}", flush=True)
            return None

    @classmethod
    def get_user_usage(cls, username):
        """دریافت میزان مصرف کاربر"""
        url = f"{cls.BASE_URL}/user/{username}/usage"
        try:
            print(f" [📊] Requesting Panel via Domain for usage: {username}", flush=True)
            response = requests.get(url, headers=cls.get_headers(), timeout=15)
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f" [!] Connection Error in get_user_usage: {str(e)}", flush=True)
            return None