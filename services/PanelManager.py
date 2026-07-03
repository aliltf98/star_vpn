# /var/www/star_vpn/services/PanelManager.py
import requests


class PanelManager:
    # 🎯 استفاده از IP مستقیم (اگر مرزبان روی سرور دیگری است، IP آن را بزن)
    # فرض می‌کنیم مرزبان روی پورت 8080 همین سرور باز است
    BASE_URL = "http://127.0.0.1:8080/api"

    ADMIN_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbWlyIiwiYWNjZXNzIjoiYWRtaW4iLCJpYXQiOjE3ODMwOTAzMTZ9.1kk4Nr3YyYrVBOMmJMrqdIW_ElzM_18AUOTQwbujC8E"

    @classmethod
    def get_headers(cls):
        return {
            "Authorization": f"Bearer {cls.ADMIN_TOKEN.strip()}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            # 🎯 هدر Host کمک می‌کند وب‌سرور بفهمد این درخواست برای کدام دامنه است
            "Host": "mediadownload.eu.org",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }

    @classmethod
    def get_user_info(cls, username):
        clean_base = cls.BASE_URL.strip()
        clean_username = str(username).strip()
        url = f"{clean_base}/user/{clean_username}"

        try:
            print(f" [🚀] Connecting Direct via IP: {url}", flush=True)
            # استفاده از http مستقیم بدون درگیری با گواهینامه SSL
            response = requests.get(url, headers=cls.get_headers(), timeout=5)
            print(f" [📥] Direct Response Code: {response.status_code}", flush=True)

            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f" [!] Connection Error in get_user_info: {str(e)}", flush=True)
            return None