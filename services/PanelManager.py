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
        return {
            "Authorization": f"Bearer {token.strip()}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    @classmethod
    def _safe_request(cls, method, endpoint, json_data=None):
        url = f"{cls.BASE_URL.strip()}/{endpoint.lstrip('/')}"
        session = cls.get_session()

        for index, token in enumerate(cls.TOKENS):
            try:
                print(f"TLS-Client Trying Token {index + 1} -> {method} {url}", flush=True)

                payload = json.dumps(json_data) if json_data else None

                if method.upper() == "POST":
                    response = session.post(url, headers=cls.get_headers(token), data=payload, timeout_seconds=15)
                elif method.upper() == "PUT":
                    response = session.put(url, headers=cls.get_headers(token), data=payload, timeout_seconds=15)
                else:
                    response = session.get(url, headers=cls.get_headers(token), timeout_seconds=15)

                print(f"TLS-Client Response Status -> {response.status_code}", flush=True)

                if response.status_code in [200, 201]:
                    return response.json()
                elif response.status_code == 403:
                    print(f" [⚠️] Token {index + 1} has no permission (403). Trying next token...", flush=True)
                    continue
                else:
                    print(f" [!] API Status: {response.status_code} | Body: {response.text}", flush=True)
                    return None

            except Exception as e:
                print(f" [❌] Connection Error with Token {index + 1}: {str(e)}", flush=True)
                continue

        print(" [❌] All tokens failed to get a successful response.", flush=True)
        return None

    @classmethod
    def create_user(cls, username, data_limit_gb=10, expire_timestamp=None):
        payload = {
            "username": str(username).strip(),
            "data_limit": int(data_limit_gb) * 1024 * 1024 * 1024,
            "data_limit_reset_strategy": "no_reset",
            "status": "active",
             "proxies": {
        "vless": {
            "flow": "xtls-rprx-vision"
        },
        "vmess": {},
        "trojan": {}
    },
    "inbounds": {
        "vless": {},
        "vmess": {},
        "trojan": {}
    }

        }
        if expire_timestamp:
            payload["expire"] = int(expire_timestamp)

        return cls._safe_request("POST", "user", json_data=payload)

    @classmethod
    def modify_user(cls, username, data_limit_gb, expire_timestamp):
        payload = {
            "data_limit": int(data_limit_gb) * 1024 * 1024 * 1024,
            "expire": int(expire_timestamp),
            "status": "active"
        }
        return cls._safe_request("PUT", f"user/{str(username).strip()}", json_data=payload)

    @classmethod
    def get_user_info(cls, username):
        return cls._safe_request("GET", f"user/{str(username).strip()}")

    @classmethod
    def get_user_usage(cls, username):
        return cls._safe_request("GET", f"user/{str(username).strip()}/usage")