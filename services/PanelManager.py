import requests

# 🎯 اتصال مستقیم به آی‌پی ابرآروان روی پورت وب (HTTP بدون s) برای دور زدن فیلترینگ و مشکلات TLS پروکسی
BASE_URL = "http://185.143.232.201:8080"
ADMIN_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJyZXphIiwiYWNjZXNzIjoiYWRtaW4iLCJpYXQiOjE3ODMwNzg4NzN9.roPZWHPSokL4PAaSAPkv7u9VtuCHe4xQoUMe4PEk3LI"


class PanelManager:

    @classmethod
    def get_headers(cls):
        """ساخت هدرهای لازم به همراه جعل هدر Host برای شناسایی توسط CDN ابرآروان"""
        return {
            "Host": "mediadownload.eu.org",  # 🎯 بسیار حیاتی برای مسیریابی در CDN
            "Authorization": f"Bearer {cls.ADMIN_TOKEN}",
            "Content-Type": "application/json"
        }

    @classmethod
    def create_user(cls, username, data_limit_gb=10):
        """ساخت کاربر جدید در پنل"""
        url = f"{cls.BASE_URL}/api/user"  # ⚠️ اگر پنل شما بخش /api/ ندارد، آن را حذف کنید
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
            print(f"➕ در حال ساخت کاربر جدید مستقیم با هدر Host: {username}")
            response = requests.post(
                url,
                json=payload,
                headers=cls.get_headers(),
                timeout=12
            )
            if response.status_code == 200:
                return response.json()
            print(f"⚠️ خطای ساخت کاربر با کد وضعیت: {response.status_code}")
            return None
        except Exception as e:
            print(f"❌ خطا در ساخت کاربر: {str(e)}")
            return None

    @staticmethod
    def get_user_info(username):
        """دریافت اطلاعات کاربر از پنل"""
        url = f"{BASE_URL}/api/user/{username}"
        try:
            print(f"🔄 ارسال مستقیم درخواست بدون پروکسی با هدر Host برای کاربر: {username}")

            response = requests.get(
                url,
                headers=PanelManager.get_headers(),
                timeout=12
            )

            print(f"📥 پاسخ پنل دریافت شد. کد وضعیت: {response.status_code}")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"⚠️ پاسخ ناموفق از پنل با کد: {response.status_code} - متن: {response.text}")
                return None
        except Exception as e:
            print(f"❌ خطا در اتصال با هدر Host به پنل: {str(e)}")
            return None

    @staticmethod
    def get_user_usage(username):
        """دریافت میزان مصرف کاربر"""
        url = f"{BASE_URL}/api/user/{username}/usage"
        try:
            print(f"📊 دریافت میزان مصرف کاربر با هدر Host: {username}")
            response = requests.get(
                url,
                headers=PanelManager.get_headers(),
                timeout=12
            )
            if response.status_code == 200:
                return response.json()
            print(f"⚠️ خطای دریافت مصرف با کد وضعیت: {response.status_code}")
            return None
        except Exception as e:
            print(f"❌ خطا در دریافت مصرف: {str(e)}")
            return None