# panelmanager.py
import requests

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
        url = f"{BASE_URL}/user/{username}"  # یا هر اندپوینتی که پنلتان دارد


        # 🎯 نکته اصلی: حتما باید متغیر proxies=PROXIES اینجا نوشته شده باشد
        response = requests.get(url, headers=headers, proxies=PROXIES, timeout=10)

        if response.status_code == 200:
            return response.json()
        return None

    @staticmethod
    def get_user_usage(username):
        url = f"{BASE_URL}/user/{username}/usage"
        response = requests.get(url, headers=headers, proxies=PROXIES, timeout=10)
        return response.json() if response.status_code == 200 else None
