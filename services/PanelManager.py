# panelmanager.py
import json
import tls_client


class PanelManager:
    BASE_URL = "https://panel.baaham.help/api"

    TOKENS = [
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJyZXphIiwiYWNjZXNzIjoiYWRtaW4iLCJpYXQiOjE3ODMxMTE2NDB9.D6a_QK6-tNOfAowIjrNtcx1H5qOcnZ82Cq9IJjZV8oM",

        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbWlyIiwiYWNjZXNzIjoiYWRtaW4iLCJpYXQiOjE3ODMxMjA1OTl9.kbwO7gDPfPabBN9QPTc0R0cxeDhXRZX6SOuzsAck5O8"

    ]

    _session = None

    @classmethod
    def get_session(cls):
        if cls._session is None:
            cls._session = tls_client.Session(client_identifier="chrome_120")
        return cls._session

    @classmethod
    def get_headers(cls, token):
        """ساخت هدر اختصاصی بر اساس توکن پاس داده شده"""
        return {
            "Authorization": f"Bearer {token.strip()}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    @classmethod
    def _safe_request(cls, method, endpoint, json_data=None):
        """ارسال درخواست و چرخش خودکار روی توکن‌ها در صورت مواجه شدن با ارور 403"""
        url = f"{cls.BASE_URL.strip()}/{endpoint.lstrip('/')}"
        session = cls.get_session()

        # 🎯 حلقه روی تک‌تک توکن‌ها برای پیدا کردن ادمین مجاز
        for index, token in enumerate(cls.TOKENS):
            try:
                print(f" [🚀] TLS-Client Trying Token {index + 1} -> {method} {url}", flush=True)

                if method.upper() == "POST":
                    payload = json.dumps(json_data) if json_data else None
                    response = session.post(url, headers=cls.get_headers(token), data=payload, timeout_seconds=15)
                else:
                    response = session.get(url, headers=cls.get_headers(token), timeout_seconds=15)

                print(f" [📥] TLS-Client Response Status -> {response.status_code}", flush=True)

                # اگر پاسخ با موفقیت همراه بود، مستقیم دیتا را برگردان
                if response.status_code in [200, 201]:
                    return response.json()

                # اگر ارور 403 داد (عدم دسترسی این ادمین به این کاربر)، توکن بعدی را در چرخه تست کن
                elif response.status_code == 403:
                    print(f" [⚠️] Token {index + 1} has no permission (403). Trying next token...", flush=True)
                    continue

                else:
                    print(f" [!] API Status: {response.status_code} | Body: {response.text}", flush=True)
                    return None

            except Exception as e:
                print(f" [❌] Connection Error with Token {index + 1}: {str(e)}", flush=True)
                continue  # اگر مشکلی در کانکشن یک توکن رخ داد، برو سراغ بعدی

        print(" [❌] All tokens failed to get a successful response.", flush=True)
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