# panelmanager.py
import requests

# 🎯 اتصال مستقیم به آی‌پی ابرآروان روی پورت وب (HTTP بدون s)
BASE_URL = "http://185.143.232.201:8080"
ADMIN_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJyZXphIiwiYWNjZXNzIjoiYWRtaW4iLCJpYXQiOjE3ODMwNzg4NzN9.roPZWHPSokL4PAaSAPkv7u9VtuCHe4xQoUMe4PEk3LI"


class PanelManager:

    @classmethod
    def get_headers(cls):
        """ساخت هدرهای کامل مرورگر برای عبور از سد فایروال و خطای 412 ابرآروان"""
        return {
            "Host": "mediadownload.eu.org",
            "Authorization": f"Bearer {ADMIN_TOKEN}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9,fa;q=0.8",
            "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "Connection": "keep-alive"
        }

    @classmethod
    def create_user(cls, username, data_limit_gb=10):
        """ساخت کاربر جدید در پنل"""
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
            print(f"➕ [PANEL] Request -> Create User: {username}", flush=True)
            response = requests.post(
                url,
                json=payload,
                headers=cls.get_headers(),
                timeout=8
            )
            print(f"📥 [PANEL] Response Status: {response.status_code}", flush=True)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"❌ [PANEL] Error creating user: {str(e)}", flush=True)
            return None

    @staticmethod
    def get_user_info(username):
        """دریافت اطلاعات کاربر از پنل"""
        url = f"{BASE_URL}/api/user/{username}"
        try:
            print(f"🚀 [PANEL] Request -> Get User Info: {username}", flush=True)

            response = requests.get(
                url,
                headers=PanelManager.get_headers(),
                timeout=8
            )

            print(f"📥 [PANEL] Response Status: {response.status_code}", flush=True)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"⚠️ [PANEL] Failed with body: {response.text[:200]}", flush=True)
                return None
        except Exception as e:
            print(f"❌ [PANEL] Connection Error: {str(e)}", flush=True)
            return None

    @staticmethod
    def get_user_usage(username):
        """دریافت میزان مصرف کاربر"""
        url = f"{BASE_URL}/api/user/{username}/usage"
        try:
            print(f"📊 [PANEL] Request -> Get Usage: {username}", flush=True)
            response = requests.get(
                url,
                headers=PanelManager.get_headers(),
                timeout=8
            )
            print(f"📥 [PANEL] Response Status: {response.status_code}", flush=True)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"❌ [PANEL] Error getting usage: {str(e)}", flush=True)
            return None