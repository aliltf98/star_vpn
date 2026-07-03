# /var/www/star_vpn/services/PanelManager.py
import requests


class PanelManager:
    # 🎯 تغییر مسیر: در داکر/لوکال مرزبان، معمولاً خود پورت مستقیماً به بخش ادمین وصل است
    # و پیشوند /api دوبار تکرار نمی‌شود.
    BASE_URL = "http://127.0.0.1:8080"

    ADMIN_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbWlyIiwiYWNjZXNzIjoiYWRtaW4iLCJpYXQiOjE3ODMwOTAzMTZ9.1kk4Nr3YyYrVBOMmJMrqdIW_ElzM_18AUOTQwbujC8E"

    @classmethod
    def get_headers(cls):
        return {
            "Authorization": f"Bearer {cls.ADMIN_TOKEN.strip()}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }

    @classmethod
    def get_user_info(cls, username):
        clean_base = cls.BASE_URL.strip()
        clean_username = str(username).strip()

        # 🎯 تست مسیر استاندارد داخلی مرزبان (/api/user/username)
        url = f"{clean_base}/api/user/{clean_username}"

        try:
            print(f" [🚀] Connecting Direct: {url}", flush=True)
            response = requests.get(url, headers=cls.get_headers(), timeout=5)
            print(f" [📥] Response Code: {response.status_code}", flush=True)

            # اگر این مسیر هم ۴۰۴ داد، مسیر زاپاس مرزبان را تست می‌کند
            if response.status_code == 404:
                alternative_url = f"{clean_base}/user/{clean_username}"
                print(f" [🔄] Trying alternative path: {alternative_url}", flush=True)
                response = requests.get(alternative_url, headers=cls.get_headers(), timeout=5)
                print(f" [📥] Alternative Response Code: {response.status_code}", flush=True)

            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f" [!] Connection Error: {str(e)}", flush=True)
            return None