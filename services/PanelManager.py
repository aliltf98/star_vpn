# panelmanager.py
import requests


class PanelManager:
    # آدرس را بدون پورت و کاملاً ساده بنویسید
    BASE_URL = "http://mediadownload.eu.org/api"

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
        # 🎯 استفاده از .strip() روی تمام متغیرها برای حذف کاراکترهای مخفی احتمالی
        clean_base = cls.BASE_URL.strip()
        clean_username = str(username).strip()
        url = f"{clean_base}/user/{clean_username}"

        try:
            print(f" [🚀] Requesting: {url}", flush=True)
            response = requests.get(url, headers=cls.get_headers(), timeout=15)
            print(f" [📥] Response Code: {response.status_code}", flush=True)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f" [!] Connection Error in get_user_info: {str(e)}", flush=True)
            return None