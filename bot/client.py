"""
Reusable REST client for the Binance Futures Testnet API.

This client communicates EXCLUSIVELY over raw HTTP using the `requests`
library. It does not depend on any Binance SDK or wrapper. It supports:

    - Public (unsigned) requests: send_public_request()
    - Private (signed) requests: send_signed_request()
    - Convenience verbs: get(), post(), delete()

Every request and response is logged, JSON is validated, and failures
are translated into the custom exception hierarchy defined in
`bot.exceptions`.
"""

from __future__ import annotations

import json
from typing import Any

import requests

from bot.auth import Credentials, create_signed_request
from bot.exceptions import (
    AuthenticationError,
    ConnectionFailedError,
    InvalidSignatureError,
    JSONParsingError,
    RateLimitError,
    ServerError,
    APIError,
)
from bot.exceptions import TimeoutError_ as BotTimeoutError
from bot.logging_config import get_logger
from bot.utils import Timer, measure_time

DEFAULT_BASE_URL = "https://testnet.binancefuture.com"
DEFAULT_TIMEOUT = 10  # seconds

# Binance error codes commonly associated with auth / signature problems.
_AUTH_ERROR_CODES = {-2014, -2015}  # Invalid API-key format / Invalid API-key, IP, or permissions
_SIGNATURE_ERROR_CODES = {-1022}  # Signature for this request is not valid


class RestClient:
    """
    A minimal, dependency-free REST client for Binance Futures Testnet.

    Attributes:
        base_url: The API base URL (default: Binance Futures Testnet).
        timeout: Request timeout in seconds.
        credentials: Optional `Credentials` for signed requests.
    """

    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.logger = get_logger()

        self.credentials: Credentials | None = None
        if api_key and api_secret:
            self.credentials = Credentials(api_key=api_key, api_secret=api_secret)

        self._session = requests.Session()

    # ------------------------------------------------------------------
    # Low-level request plumbing
    # ------------------------------------------------------------------
    def _full_url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def _log_request(
        self, method: str, url: str, headers: dict[str, str], params: dict[str, Any] | None
    ) -> None:
        safe_headers = {k: ("***REDACTED***" if k == "X-MBX-APIKEY" else v) for k, v in headers.items()}
        self.logger.debug(
            "REQUEST | method=%s | url=%s | headers=%s | params=%s",
            method,
            url,
            safe_headers,
            params,
        )

    def _log_response(self, response: requests.Response, elapsed_ms: float) -> None:
        self.logger.debug(
            "RESPONSE | status=%s | elapsed_ms=%.2f | body=%s",
            response.status_code,
            elapsed_ms,
            response.text[:2000],  # avoid flooding logs with huge bodies
        )

    def _parse_json(self, response: requests.Response) -> Any:
        try:
            return response.json()
        except (json.JSONDecodeError, ValueError) as exc:
            self.logger.error("Failed to parse JSON response: %s", response.text[:500])
            raise JSONParsingError(
                f"Could not parse JSON from response (status={response.status_code}): "
                f"{response.text[:200]}"
            ) from exc

    def _raise_for_status(self, response: requests.Response, parsed: Any) -> None:
        """Translate non-2xx responses and Binance error payloads into exceptions."""
        status = response.status_code

        error_code = None
        message = ""
        if isinstance(parsed, dict):
            error_code = parsed.get("code")
            message = parsed.get("msg", "")

        if status == 200:
            return

        if status == 429 or status == 418:
            raise RateLimitError(status, error_code, message or "Rate limit exceeded.")

        if status in _AUTH_ERROR_CODES or error_code in _AUTH_ERROR_CODES:
            raise AuthenticationError(status, error_code, message or "Authentication failed.")

        if error_code in _SIGNATURE_ERROR_CODES:
            raise InvalidSignatureError(status, error_code, message or "Invalid signature.")

        if 500 <= status < 600:
            raise ServerError(status, error_code, message or "Binance server error.")

        if status == 401 or status == 403:
            raise AuthenticationError(status, error_code, message or "Unauthorized.")

        # Generic fallback for any other 4xx/5xx.
        raise APIError(status, error_code, message or f"Request failed with status {status}.")

    def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        """
        Perform a raw HTTP request and return the parsed JSON body.

        Args:
            method: HTTP method ("GET", "POST", "DELETE").
            path: API path, e.g. "/fapi/v1/order".
            params: Query parameters.
            headers: Extra HTTP headers (e.g. X-MBX-APIKEY).

        Returns:
            The parsed JSON response body.

        Raises:
            ConnectionFailedError: On network/connection failure.
            BotTimeoutError: On request timeout.
            APIError (or subclass): On non-2xx / Binance error responses.
            JSONParsingError: If the response body is not valid JSON.
        """
        url = self._full_url(path)
        headers = headers or {}
        params = params or {}

        self._log_request(method, url, headers, params)

        timer = Timer()
        try:
            with measure_time(timer):
                response = self._session.request(
                    method=method,
                    url=url,
                    params=params if method == "GET" else None,
                    data=params if method in ("POST", "DELETE") else None,
                    headers=headers,
                    timeout=self.timeout,
                )
        except requests.exceptions.Timeout as exc:
            self.logger.error("Request timed out: %s %s", method, url)
            raise BotTimeoutError(f"Request to {url} timed out after {self.timeout}s.") from exc
        except requests.exceptions.ConnectionError as exc:
            self.logger.error("Connection failed: %s %s | %s", method, url, exc)
            raise ConnectionFailedError(f"Could not connect to {url}: {exc}") from exc
        except requests.exceptions.RequestException as exc:
            self.logger.error("Unexpected request exception: %s %s | %s", method, url, exc)
            raise ConnectionFailedError(f"Request to {url} failed: {exc}") from exc

        self._log_response(response, timer.elapsed_ms)

        parsed = self._parse_json(response)
        self._raise_for_status(response, parsed)

        return parsed

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def send_public_request(
        self, method: str, path: str, params: dict[str, Any] | None = None
    ) -> Any:
        """
        Send an unsigned (public) request to a Binance endpoint.

        Args:
            method: HTTP method ("GET", "POST", "DELETE").
            path: API path, e.g. "/fapi/v1/ping".
            params: Optional query parameters.

        Returns:
            The parsed JSON response body.
        """
        return self._request(method=method, path=path, params=params)

    def send_signed_request(
        self, method: str, path: str, params: dict[str, Any] | None = None
    ) -> Any:
        """
        Send a signed (private) request to a Binance endpoint.

        Automatically attaches `timestamp`, `recvWindow`, and `signature`
        to the parameters, and sends the API key via the `X-MBX-APIKEY`
        header.

        Args:
            method: HTTP method ("GET", "POST", "DELETE").
            path: API path, e.g. "/fapi/v2/account".
            params: Base parameters (without timestamp/signature).

        Returns:
            The parsed JSON response body.

        Raises:
            ConfigurationError: If no credentials were configured on this client.
        """
        if self.credentials is None:
            from bot.exceptions import ConfigurationError

            raise ConfigurationError(
                "This client was not configured with API credentials. "
                "Provide api_key and api_secret to RestClient()."
            )

        signed = create_signed_request(params or {}, self.credentials)

        # Rebuild params as a dict so requests can encode consistently,
        # while preserving the exact signed query string ordering by
        # passing the pre-built query string directly via `params=None`
        # and appending it to the URL instead.
        url_path = f"{path}?{signed.full_query_string}"

        return self._request(method=method, path=url_path, params=None, headers=signed.headers)

    # Convenience verb wrappers -----------------------------------------
    def get(self, path: str, params: dict[str, Any] | None = None, signed: bool = False) -> Any:
        """Send a GET request, signed or public depending on `signed`."""
        if signed:
            return self.send_signed_request("GET", path, params)
        return self.send_public_request("GET", path, params)

    def post(self, path: str, params: dict[str, Any] | None = None, signed: bool = True) -> Any:
        """Send a POST request, signed by default (most POST endpoints require auth)."""
        if signed:
            return self.send_signed_request("POST", path, params)
        return self.send_public_request("POST", path, params)

    def delete(self, path: str, params: dict[str, Any] | None = None, signed: bool = True) -> Any:
        """Send a DELETE request, signed by default (most DELETE endpoints require auth)."""
        if signed:
            return self.send_signed_request("DELETE", path, params)
        return self.send_public_request("DELETE", path, params)
