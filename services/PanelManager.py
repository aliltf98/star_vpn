import requests

class PanelManager:
    BASE_URL = "https://mediadownload.eu.org/api"
    # اگر پنل نیاز به توکن ادمین دارد (معمولاً Marzban نیاز دارد)
    ADMIN_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJyZXphIiwiYWNjZXNzIjoiYWRtaW4iLCJpYXQiOjE3NzY4NTExMjR9.90CzZtHSdb8I7PJUNs-nE7hrD1YRQ_b311zSCWY1lBA"

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
            "data_limit": data_limit_gb * 1024 * 1024 * 1024, # تبدیل گیگ به بایت
            "status": "active",
            "proxies": {"vless": {}, "vmess": {}, "trojan": {}},
            "inbounds": {
                "vless": ["VLESS TCP REALITY", "VLESS GRPC REALITY"],
                "vmess": ["VMess TCP", "VMess Websocket"]
            }
        }
        response = requests.post(url, json=payload, headers=cls.get_headers())
        return response.json() if response.status_code == 200 else None

    @classmethod
    def get_user_info(cls, username):
        """گرفتن اطلاعات کامل و لینک‌های کاربر"""
        url = f"{cls.BASE_URL}/user/{username}"
        response = requests.get(url, headers=cls.get_headers())
        if response.status_code == 200:
            return response.json()
        return None

    @classmethod
    def get_user_usage(cls, username):
        """گرفتن میزان مصرف به تفکیک نودها"""
        url = f"{cls.BASE_URL}/user/{username}/usage"
        response = requests.get(url, headers=cls.get_headers())
        return response.json() if response.status_code == 200 else None