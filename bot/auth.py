"""
Manual HMAC-SHA256 authentication for Binance Futures REST API.

Binance requires signed requests for private endpoints. The signing
process is:

    1. Build the query string from parameters (sorted is NOT required
       by Binance, but we preserve insertion order as given).
    2. Compute HMAC-SHA256 of the query string using the API secret
       as the key.
    3. Append the resulting hex digest as a `signature` parameter.
    4. Send the API key in the `X-MBX-APIKEY` header.

No third-party Binance SDKs are used; only `hmac`, `hashlib`, and
`urllib.parse` from the standard library.
"""

from __future__ import annotations

import hashlib
import hmac
import time
import urllib.parse
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Credentials:
    """Holds the API key and secret used to sign requests."""

    api_key: str
    api_secret: str

    def __post_init__(self) -> None:
        if not self.api_key or not self.api_secret:
            raise ValueError(
                "Both api_key and api_secret must be non-empty. "
                "Check your .env file."
            )


def get_timestamp_ms() -> int:
    """Return the current Unix timestamp in milliseconds, as required by Binance."""
    return int(time.time() * 1000)


def build_query_string(params: dict[str, Any]) -> str:
    """
    Build a URL-encoded query string from a parameter dictionary.

    Args:
        params: Mapping of parameter names to values. Values are cast
            to strings before encoding.

    Returns:
        A URL-encoded query string, e.g. "symbol=BTCUSDT&side=BUY".
    """
    filtered = {k: v for k, v in params.items() if v is not None}
    return urllib.parse.urlencode(filtered, doseq=True)


def sign_query_string(query_string: str, api_secret: str) -> str:
    """
    Compute the HMAC-SHA256 signature of a query string.

    Args:
        query_string: The URL-encoded query string to sign.
        api_secret: The Binance API secret used as the HMAC key.

    Returns:
        The hex-encoded HMAC-SHA256 signature.
    """
    return hmac.new(
        key=api_secret.encode("utf-8"),
        msg=query_string.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()


@dataclass
class SignedRequest:
    """Represents a fully-signed request ready to be sent."""

    query_string: str
    signature: str
    headers: dict[str, str] = field(default_factory=dict)

    @property
    def full_query_string(self) -> str:
        """Return the query string with the signature parameter appended."""
        return f"{self.query_string}&signature={self.signature}"


def create_signed_request(
    params: dict[str, Any],
    credentials: Credentials,
    recv_window: int = 5000,
) -> SignedRequest:
    """
    Build a fully-signed request from a parameter dictionary.

    Adds `timestamp` and `recvWindow` to the parameters, computes the
    HMAC-SHA256 signature, and prepares the `X-MBX-APIKEY` header.

    Args:
        params: Base request parameters (without timestamp/signature).
        credentials: API key/secret pair.
        recv_window: Number of milliseconds the request is valid for
            after the timestamp (Binance default is 5000).

    Returns:
        A `SignedRequest` containing the query string, signature, and headers.
    """
    full_params = dict(params)
    full_params["timestamp"] = get_timestamp_ms()
    full_params["recvWindow"] = recv_window

    query_string = build_query_string(full_params)
    signature = sign_query_string(query_string, credentials.api_secret)

    headers = {"X-MBX-APIKEY": credentials.api_key}

    return SignedRequest(query_string=query_string, signature=signature, headers=headers)
