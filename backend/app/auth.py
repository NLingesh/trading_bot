import hashlib, hmac, time
from typing import Any, Dict

def get_timestamp() -> int:
    return int(time.time() * 1000)

def build_query_string(params: Dict[str, Any]) -> str:
    return "&".join(f"{k}={v}" for k, v in params.items())

def sign(query_string: str, secret: str) -> str:
    return hmac.new(secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()

def build_signed_params(params: Dict[str, Any], secret: str) -> Dict[str, Any]:
    params["timestamp"] = get_timestamp()
    params["signature"] = sign(build_query_string(params), secret)
    return params

def get_auth_headers(api_key: str) -> Dict[str, str]:
    return {"X-MBX-APIKEY": api_key}
