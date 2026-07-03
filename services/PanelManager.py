# panelmanager.py
import requests

# 🎯 آدرس اصلی و استاندارد پنل شما
BASE_URL = "http://185.143.232.201:8080"
ADMIN_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJyZXphIiwiYWNjZXNzIjoiYWRtaW4iLCJpYXQiOjE3ODMwNzg4NzN9.roPZWHPSokL4PAaSAPkv7u9VtuCHe4xQoUMe4PEk3LI"

class PanelManager:

    @classmethod
    def get_headers(cls):
        """هدرهای اصلی و استاندارد بدون هیچگونه دستکاری مرورگر"""
        return {
            "Host": "mediadownload.eu.org",  # برای مسیریابی درست در شبکه ابرآروان
            "Authorization": f"Bearer {ADMIN_TOKEN}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    @classmethod
    def create_user(cls, username, data_limit_gb=10):
        url = f"{cls.BASE_URL}/api/user"
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
            print(f" [+] API Request -> Creating user: {username}", flush=True)
            response = requests.post(url, json=payload, headers=cls.get_headers(), timeout=10)
            print(f" [-] API Response Status: {response.status_code}", flush=True)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f" [!] API Error: {str(e)}", flush=True)
            return None

    @staticmethod
    def get_user_info(username):
        url = f"{BASE_URL}/api/user/{username}"
        try:
            print(f" [🚀] API Request -> Getting info for: {username}", flush=True)
            response = requests.get(url, headers=PanelManager.get_headers(), timeout=10)
            print(f" [📥] API Response Status: {response.status_code}", flush=True)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f" [!] Connection Error: {str(e)}", flush=True)
            return None