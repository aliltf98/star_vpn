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
        url = f"{BASE_URL}/user/{username}"


        try:
            print(f"🔄 در حال ارسال درخواست به پنل برای کاربر: {username} از طریق پروکسی...")

            # ارسال درخواست همراه با پروکسی و هدرها
            response = requests.get(url, headers=headers, proxies=PROXIES, timeout=12)

            print(f"📥 پاسخ پنل دریافت شد. کد وضعیت: {response.status_code}")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"⚠️ پنل پاسخ داد اما با کد خطا: {response.text}")
                return None

        except requests.exceptions.ProxyError as pe:
            print(f"❌ خطای پروکسی (ProxyError): اطلاعات اتصال یا یوزر/پسورد پروکسی اشتباه است! جزییات: {pe}")
        except requests.exceptions.Timeout:
            print("❌ خطای زمان (Timeout): پروکسی یا سرور پنل بعد از ۱۲ ثانیه پاسخ ندادند.")
        except requests.exceptions.ConnectionError as ce:
            print(f"❌ خطای فیزیکی اتصال (ConnectionError): پروکسی روی پورت 110 فعال نیست یا کرش کرده است! جزییات: {ce}")
        except Exception as e:
            print(f"❌ خطای ناشناخته در پنل منیجر: {str(e)}")

        return None

    @staticmethod
    def get_user_usage(username):
        url = f"{BASE_URL}/user/{username}/usage"
        response = requests.get(url, headers=headers, proxies=PROXIES, timeout=10)
        return response.json() if response.status_code == 200 else None
