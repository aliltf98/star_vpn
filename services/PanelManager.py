# /var/www/star_vpn/services/PanelManager.py
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import connection
import urllib3

# خاموش کردن هشدارهای SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 🎯 ترفند تزریق DNS دستی: دامین را مستقیماً به لوکال‌هست متصل می‌کنیم روی پورت امن
_orig_create_connection = connection.create_connection


def patched_create_connection(address, *args, **kwargs):
    host, port = address
    if host == "mediadownload.eu.org":
        # هدایت ترافیک دامین به آی‌پد داخلی سرور (جایی که وب‌سرور ادمین مرزبان گوش می‌دهد)
        return _orig_create_connection(("127.0.0.1", port), *args, **kwargs)
    return _orig_create_connection(address, *args, **kwargs)


connection.create_connection = patched_create_connection


class PanelManager:
    # بازگشت به همان آدرس استاندارد ادمین که در Swagger کار می‌کرد
    BASE_URL = "https://mediadownload.eu.org/api"

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
        url = f"{cls.BASE_URL.strip()}/user/{str(username).strip()}"

        try:
            print(f" [🚀] Requesting via DNS Patch: {url}", flush=True)
            # استفاده از verify=False برای عبور از سد فایروال محلی
            response = requests.get(url, headers=cls.get_headers(), timeout=10, verify=False)
            print(f" [📥] Response Code: {response.status_code}", flush=True)

            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f" [!] Connection Error: {str(e)}", flush=True)
            return None