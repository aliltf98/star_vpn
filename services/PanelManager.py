# panelmanager.py
import json
import tls_client


class PanelManager:
    BASE_URL = "https://panel.baaham.help/api"
    ADMIN_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJyZXphIiwiYWNjZXNzIjoiYWRtaW4iLCJpYXQiOjE3ODMxMTE2NDB9.D6a_QK6-tNOfAowIjrNtcx1H5qOcnZ82Cq9IJjZV8oM"

    _session = None

    @classmethod
    def get_session(cls):
        if cls._session is None:
            # 🎯 شبیه‌سازی دقیق مرورگر کروم ۱۲۰ بدون هیچ‌گونه پروکسی
            cls._session = tls_client.Session(
                client_identifier="chrome_120"
            )
        return cls._session

    @classmethod
    def get_headers(cls):
        return {
            "Authorization": f"Bearer {cls.ADMIN_TOKEN.strip()}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    @classmethod
    def _safe_request(cls, method, endpoint, json_data=None):
        """ارسال امن درخواست‌ها مستقیم و بدون پروکسی"""
        url = f"{cls.BASE_URL.strip()}/{endpoint.lstrip('/')}"
        session = cls.get_session()

        try:
            print(f" [🚀] TLS-Client Direct Request -> {method} {url}", flush=True)

            if method.upper() == "POST":
                payload = json.dumps(json_data) if json_data else None
                response = session.post(url, headers=cls.get_headers(), data=payload, timeout_seconds=15)
            else:
                response = session.get(url, headers=cls.get_headers(), timeout_seconds=15)

            print(f" [📥] TLS-Client Direct Response Status -> {response.status_code}", flush=True)

            if response.status_code in [200, 201]:
                return response.json()
            else:
                print(f" [!] API Status: {response.status_code} | Body: {response.text}", flush=True)
                return None
        except Exception as e:
            print(f" [❌] Direct Connection Error: {str(e)}", flush=True)
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