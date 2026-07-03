# panelmanager.py
import requests

class PanelManager:
    # 🎯 اتصال مستقیم به آی‌پی سرورِ پنل روی پورت HTTP بدون SSL و کلودفلر
    BASE_URL = "http://185.143.232.201:8080/api"
    ADMIN_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJyZXphIiwiYWNjZXNzIjoiYWRtaW4iLCJpYXQiOjE3ODMwNzg4NzN9.roPZWHPSokL4PAaSAPkv7u9VtuCHe4xQoUMe4PEk3LI"

    @classmethod
    def get_headers(cls):
        return {
            "Authorization": f"Bearer {cls.ADMIN_TOKEN}",
            "Content-Type": "application/json",
            "Accept": "application/json"
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
            print(f" [+] Connecting directly to Panel IP for creating: {username}", flush=True)
            response = requests.post(url, json=payload, headers=cls.get_headers(), timeout=10)
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
            print(f" [🚀] Connecting directly to Panel IP for info: {username}", flush=True)
            response = requests.get(url, headers=cls.get_headers(), timeout=10)
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
            print(f" [📊] Connecting directly to Panel IP for usage: {username}", flush=True)
            response = requests.get(url, headers=cls.get_headers(), timeout=10)
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f" [!] Connection Error in get_user_usage: {str(e)}", flush=True)
            return None