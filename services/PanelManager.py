# panelmanager.py
import requests


class PanelManager:
    BASE_URL = "https://mediadownload.eu.org/api"
    ADMIN_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJyZXphIiwiYWNjZXNzIjoiYWRtaW4iLCJpYXQiOjE3ODMwNzg4NzN9.roPZWHPSokL4PAaSAPkv7u9VtuCHe4xQoUMe4PEk3LI"

    PROXIES = {
        'http': 'http://m0kvE6Vpqz22:K0oRxaoNfz22@188.121.97.153:110',
        'https': 'https://m0kvE6Vpqz22:K0oRxaoNfz22@188.121.97.153:110',
    }

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

    @classmethod
    def get_user_info(cls, username):
        url = f"{cls.BASE_URL}/user/{username}"
        response = requests.get(
            url,
            headers=cls.get_headers(),
            proxies=cls.PROXIES,
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return None

    @classmethod
    def get_user_usage(cls, username):
        url = f"{cls.BASE_URL}/user/{username}/usage"
        response = requests.get(
            url,
            headers=cls.get_headers(),
            proxies=cls.PROXIES,
            timeout=10
        )
        return response.json() if response.status_code == 200 else None
