"""
Input validation utilities for the trading bot.

All functions raise a specific subclass of `ValidationError` (see
`bot.exceptions`) with a meaningful message when validation fails.
"""

from __future__ import annotations

import re

from bot.exceptions import (
    InvalidOrderTypeError,
    InvalidPriceError,
    InvalidQuantityError,
    InvalidSideError,
    InvalidSymbolError,
)

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}

# Binance Futures symbols are uppercase alphanumeric, e.g. BTCUSDT, ETHUSDT.
_SYMBOL_PATTERN = re.compile(r"^[A-Z0-9]{5,20}$")


def validate_symbol(symbol: str) -> str:
    """
    Validate a trading symbol.

    Args:
        symbol: The symbol to validate, e.g. "BTCUSDT".

    Returns:
        The normalized (uppercase, stripped) symbol.

    Raises:
        InvalidSymbolError: If the symbol is empty or malformed.
    """
    if not symbol or not isinstance(symbol, str):
        raise InvalidSymbolError("Symbol must be a non-empty string.")

    normalized = symbol.strip().upper()

    if not _SYMBOL_PATTERN.match(normalized):
        raise InvalidSymbolError(
            f"Symbol {symbol!r} is invalid. Expected an uppercase alphanumeric "
            f"symbol between 5 and 20 characters (e.g. BTCUSDT)."
        )

    return normalized


def validate_side(side: str) -> str:
    """
    Validate an order side.

    Args:
        side: The order side, expected to be "BUY" or "SELL".

    Returns:
        The normalized (uppercase, stripped) side.

    Raises:
        InvalidSideError: If the side is not BUY or SELL.
    """
    if not side or not isinstance(side, str):
        raise InvalidSideError("Side must be a non-empty string.")

    normalized = side.strip().upper()

    if normalized not in VALID_SIDES:
        raise InvalidSideError(
            f"Side {side!r} is invalid. Must be one of {sorted(VALID_SIDES)}."
        )

    return normalized


def validate_order_type(order_type: str) -> str:
    """
    Validate an order type.

    Args:
        order_type: The order type, expected to be "MARKET" or "LIMIT".

    Returns:
        The normalized (uppercase, stripped) order type.

    Raises:
        InvalidOrderTypeError: If the order type is not MARKET or LIMIT.
    """
    if not order_type or not isinstance(order_type, str):
        raise InvalidOrderTypeError("Order type must be a non-empty string.")

    normalized = order_type.strip().upper()

    if normalized not in VALID_ORDER_TYPES:
        raise InvalidOrderTypeError(
            f"Order type {order_type!r} is invalid. "
            f"Must be one of {sorted(VALID_ORDER_TYPES)}."
        )

    return normalized


def validate_quantity(quantity: float | str | None) -> float:
    """
    Validate an order quantity.

    Args:
        quantity: The quantity to validate. Must be a positive number.

    Returns:
        The quantity as a float.

    Raises:
        InvalidQuantityError: If the quantity is missing, non-numeric,
            or not strictly positive.
    """
    if quantity is None:
        raise InvalidQuantityError("Quantity is required.")

    try:
        value = float(quantity)
    except (TypeError, ValueError) as exc:
        raise InvalidQuantityError(f"Quantity {quantity!r} is not a valid number.") from exc

    if value <= 0:
        raise InvalidQuantityError(f"Quantity must be positive, got {value}.")

    return value


def validate_price(price: float | str | None, order_type: str) -> float | None:
    """
    Validate an order price, required only for LIMIT orders.

    Args:
        price: The price to validate. May be None for MARKET orders.
        order_type: The already-normalized order type ("MARKET" or "LIMIT").

    Returns:
        The price as a float, or None for MARKET orders.

    Raises:
        InvalidPriceError: If order_type is LIMIT and price is missing,
            non-numeric, or not strictly positive.
    """
    if order_type == "MARKET":
        return None

    if price is None:
        raise InvalidPriceError("Price is required for LIMIT orders.")

    try:
        value = float(price)
    except (TypeError, ValueError) as exc:
        raise InvalidPriceError(f"Price {price!r} is not a valid number.") from exc

    if value <= 0:
        raise InvalidPriceError(f"Price must be positive, got {value}.")

    return value
