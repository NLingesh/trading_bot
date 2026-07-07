import logging
from typing import Any, Dict, Optional
import requests
from app.auth import build_signed_params, get_auth_headers
from app.exceptions import BinanceAPIError, NetworkError

logger = logging.getLogger("trading_bot")

class BinanceRestClient:
    def __init__(self, api_key: str, api_secret: str, base_url: str, timeout: int = 10):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()
        if api_key:
            self._session.headers.update(get_auth_headers(api_key))

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def _parse(self, response: requests.Response) -> Any:
        logger.info("← %s %s", response.status_code, response.url)
        try:
            data = response.json()
        except ValueError:
            raise NetworkError(f"Non-JSON response: {response.text[:200]}")
        if isinstance(data, dict) and isinstance(data.get("code"), int) and data["code"] < 0:
            raise BinanceAPIError(code=data["code"], message=data.get("msg", ""), http_status=response.status_code)
        if not response.ok:
            raise BinanceAPIError(code=response.status_code, message=response.text[:200], http_status=response.status_code)
        return data

    def _req(self, method: str, path: str, params: Dict[str, Any]) -> Any:
        url = self._url(path)
        logger.info("→ %s %s %s", method, url, {k: v for k, v in params.items() if k != "signature"})
        try:
            r = self._session.request(method, url, params=params, timeout=self.timeout)
        except requests.exceptions.Timeout:
            raise NetworkError(f"Timeout: {method} {url}")
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Connection error: {e}")
        return self._parse(r)

    def get(self, path: str, params: Optional[Dict] = None, signed: bool = False) -> Any:
        p = dict(params or {})
        if signed: p = build_signed_params(p, self.api_secret)
        return self._req("GET", path, p)

    def post(self, path: str, params: Dict, signed: bool = True) -> Any:
        p = dict(params)
        if signed: p = build_signed_params(p, self.api_secret)
        return self._req("POST", path, p)

    def delete(self, path: str, params: Dict, signed: bool = True) -> Any:
        p = dict(params)
        if signed: p = build_signed_params(p, self.api_secret)
        return self._req("DELETE", path, p)
