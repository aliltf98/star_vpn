# panelmanager.py
import requests
import urllib3

# خاموش کردن هشدارهای SSL در لاگ سرور
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class PanelManager:
    BASE_URL = "https://panel.baaham.help/api"
    ADMIN_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJyZXphIiwiYWNjZXNzIjoiYWRtaW4iLCJpYXQiOjE3ODMxMTE2NDB9.D6a_QK6-tNOfAowIjrNtcx1H5qOcnZ82Cq9IJjZV8oM"

    # 🎯 تعریف بهینه پروکسی (پشتیبانی همزمان از http و socks5 در صورت نیاز)
    PROXIES = {
        'http': 'http://m0kvE6Vpqz22:K0oRxaoNfz22@127.0.0.1:110',
        'https': 'http://m0kvE6Vpqz22:K0oRxaoNfz22@127.0.0.1:110',
    }

    # 🎯 استفاده از یک Session پایدار برای کاهش مصرف CPU و سرعت بالاتر ارتباطات
    _session = None

    @classmethod
    def get_session(cls):
        if cls._session is None:
            cls._session = requests.Session()
            cls._session.proxies = cls.PROXIES
            # نادیده گرفتن خطاهای SSL ناشی از شتاب‌دهنده‌ها یا پروکسی‌ها
            cls._session.verify = False
        return cls._session

    @classmethod
    def get_headers(cls):
        return {
            "Authorization": f"Bearer {cls.ADMIN_TOKEN.strip()}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    @classmethod
    def _safe_request(cls, method, endpoint, json_data=None):
        """متد داخلی و امن برای ارسال تمام درخواست‌ها با مدیریت خطای پیشرفته"""
        url = f"{cls.BASE_URL.strip()}/{endpoint.lstrip('/')}"
        session = cls.get_session()

        try:
            print(f" [🚀] Marzban API Request -> {method} {url}", flush=True)
            response = session.request(
                method=method,
                url=url,
                headers=cls.get_headers(),
                json=json_data,
                timeout=12  # تایم‌اوت بهینه برای پروکسی‌های داخلی
            )
            print(f" [📥] Marzban Response Status -> {response.status_code}", flush=True)

            if response.status_code in [200, 201]:
                return response.json()
            else:
                print(f" [!] API returned non-200 status: {response.status_code} | Body: {response.text}", flush=True)
                return None
        except requests.exceptions.ProxyError as pe:
            print(f" [❌] Proxy Connection Failed! Check your 127.0.0.1:110 proxy status. Error: {str(pe)}", flush=True)
            return None
        except Exception as e:
            print(f" [❌] Network/Timeout Error in Marzban connection: {str(e)}", flush=True)
            return None

    @classmethod
    def create_user(cls, username, data_limit_gb=10):
        """ساخت کاربر جدید در پنل مرزبان"""
        payload = {
            "username": str(username).strip(),
            "data_limit": int(data_limit_gb) * 1024 * 1024 * 1024,
            "status": "active",
            "proxies": {"vless": {}, "vmess": {}, "trojan": {}},
            "inbounds": {
                "vless": ["VLESS TCP REALITY", "VLESS GRPC REALITY"],
                "vmess": ["VMess TCP", "VMess Websocket"]
            }
        }
        return cls._safe_request("POST", "user", json_data=payload)

    @classmethod
    def get_user_info(cls, username):
        """دریافت اطلاعات کامل کاربر"""
        return cls._safe_request("GET", f"user/{str(username).strip()}")

    @classmethod
    def get_user_usage(cls, username):
        """دریافت میزان مصرف کاربر"""
        return cls._safe_request("GET", f"user/{str(username).strip()}/usage")