"""
Miscellaneous helper utilities: timing, response formatting, and env loading.
"""

from __future__ import annotations

import os
import time
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterator

from bot.exceptions import ConfigurationError


@dataclass
class Timer:
    """Simple millisecond-precision execution timer."""

    start_time: float = 0.0
    elapsed_ms: float = 0.0


@contextmanager
def measure_time(timer: Timer) -> Iterator[None]:
    """
    Context manager that measures elapsed wall-clock time in milliseconds.

    Args:
        timer: A `Timer` instance whose `elapsed_ms` will be populated.
    """
    timer.start_time = time.perf_counter()
    try:
        yield
    finally:
        timer.elapsed_ms = (time.perf_counter() - timer.start_time) * 1000


def ms_to_iso(timestamp_ms: int | None) -> str:
    """
    Convert a Binance millisecond timestamp to an ISO-8601 UTC string.

    Args:
        timestamp_ms: Milliseconds since epoch, or None.

    Returns:
        An ISO-8601 formatted UTC datetime string, or "N/A" if input is None.
    """
    if timestamp_ms is None:
        return "N/A"
    return datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc).strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )


def require_env(name: str) -> str:
    """
    Fetch a required environment variable.

    Args:
        name: The environment variable name.

    Returns:
        The variable's value.

    Raises:
        ConfigurationError: If the variable is not set or empty.
    """
    value = os.getenv(name)
    if not value:
        raise ConfigurationError(
            f"Environment variable {name!r} is not set. "
            f"Copy .env.example to .env and fill in your credentials."
        )
    return value


def format_order_summary(order: dict) -> str:
    """
    Format an order response dictionary into a human-readable summary block.

    Args:
        order: The parsed JSON response from a Binance order endpoint.

    Returns:
        A multi-line, readable string suitable for console output.
    """
    symbol = order.get("symbol", "N/A")
    order_id = order.get("orderId", "N/A")
    status = order.get("status", "N/A")
    side = order.get("side", "N/A")
    order_type = order.get("type", "N/A")
    executed_qty = order.get("executedQty", "N/A")
    orig_qty = order.get("origQty", "N/A")
    avg_price = order.get("avgPrice", "N/A")
    price = order.get("price", "N/A")
    update_time = order.get("updateTime")

    lines = [
        "=" * 50,
        " ORDER SUMMARY",
        "=" * 50,
        f" Symbol            : {symbol}",
        f" Order ID          : {order_id}",
        f" Side              : {side}",
        f" Type              : {order_type}",
        f" Status            : {status}",
        f" Requested Qty     : {orig_qty}",
        f" Executed Qty      : {executed_qty}",
        f" Price             : {price}",
        f" Average Price     : {avg_price}",
        f" Time              : {ms_to_iso(update_time)}",
        "=" * 50,
    ]
    return "\n".join(lines)
