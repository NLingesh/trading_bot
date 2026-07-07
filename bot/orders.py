"""
High-level Binance Futures Testnet endpoint wrappers.

This module implements the specific REST endpoints required by the
trading bot, built on top of the low-level `RestClient`. All endpoint
paths and parameters follow the official Binance Futures API reference.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from bot.client import RestClient
from bot.logging_config import get_logger
from bot.validators import (
    validate_order_type,
    validate_price,
    validate_quantity,
    validate_side,
    validate_symbol,
)

logger = get_logger()


@dataclass
class OrderRequest:
    """Normalized, validated representation of an order to be placed."""

    symbol: str
    side: str
    order_type: str
    quantity: float
    price: float | None = None

    @classmethod
    def from_raw(
        cls,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float | str,
        price: float | str | None = None,
    ) -> "OrderRequest":
        """Build and validate an `OrderRequest` from raw (possibly stringly-typed) inputs."""
        norm_symbol = validate_symbol(symbol)
        norm_side = validate_side(side)
        norm_type = validate_order_type(order_type)
        norm_qty = validate_quantity(quantity)
        norm_price = validate_price(price, norm_type)

        return cls(
            symbol=norm_symbol,
            side=norm_side,
            order_type=norm_type,
            quantity=norm_qty,
            price=norm_price,
        )


class BinanceFuturesEndpoints:
    """
    Wraps the specific Binance Futures Testnet REST endpoints used by this bot.

    All methods return the parsed JSON response as a dict/list, exactly
    as returned by Binance.
    """

    def __init__(self, client: RestClient) -> None:
        self.client = client

    # ------------------------------------------------------------------
    # Public / market data endpoints
    # ------------------------------------------------------------------
    def ping(self) -> dict:
        """
        Test connectivity to the REST API.

        Endpoint: GET /fapi/v1/ping
        """
        logger.info("Pinging Binance Futures Testnet...")
        return self.client.get("/fapi/v1/ping", signed=False)

    def get_server_time(self) -> dict:
        """
        Get the current Binance server time.

        Endpoint: GET /fapi/v1/time
        """
        logger.info("Fetching server time...")
        return self.client.get("/fapi/v1/time", signed=False)

    def get_exchange_info(self) -> dict:
        """
        Get exchange trading rules and symbol information.

        Endpoint: GET /fapi/v1/exchangeInfo
        """
        logger.info("Fetching exchange information...")
        return self.client.get("/fapi/v1/exchangeInfo", signed=False)

    # ------------------------------------------------------------------
    # Account / position endpoints (signed)
    # ------------------------------------------------------------------
    def get_account_info(self) -> dict:
        """
        Get current account information (balances, positions, permissions).

        Endpoint: GET /fapi/v2/account (signed)
        """
        logger.info("Fetching account information...")
        return self.client.get("/fapi/v2/account", signed=True)

    def get_position_info(self, symbol: str | None = None) -> list:
        """
        Get current position information.

        Endpoint: GET /fapi/v2/positionRisk (signed)

        Args:
            symbol: Optional symbol filter, e.g. "BTCUSDT".
        """
        params: dict[str, Any] = {}
        if symbol:
            params["symbol"] = validate_symbol(symbol)
        logger.info("Fetching position information for symbol=%s...", symbol or "ALL")
        return self.client.get("/fapi/v2/positionRisk", params=params, signed=True)

    def get_open_orders(self, symbol: str | None = None) -> list:
        """
        Get all open orders on a symbol (or all symbols).

        Endpoint: GET /fapi/v1/openOrders (signed)

        Args:
            symbol: Optional symbol filter, e.g. "BTCUSDT".
        """
        params: dict[str, Any] = {}
        if symbol:
            params["symbol"] = validate_symbol(symbol)
        logger.info("Fetching open orders for symbol=%s...", symbol or "ALL")
        return self.client.get("/fapi/v1/openOrders", params=params, signed=True)

    def get_order_status(self, symbol: str, order_id: int) -> dict:
        """
        Check the status of an individual order.

        Endpoint: GET /fapi/v1/order (signed)

        Args:
            symbol: Trading symbol, e.g. "BTCUSDT".
            order_id: The Binance-assigned order ID to query.
        """
        norm_symbol = validate_symbol(symbol)
        logger.info("Fetching order status for symbol=%s, orderId=%s...", norm_symbol, order_id)
        return self.client.get(
            "/fapi/v1/order",
            params={"symbol": norm_symbol, "orderId": order_id},
            signed=True,
        )

    def cancel_order(self, symbol: str, order_id: int) -> dict:
        """
        Cancel an active order.

        Endpoint: DELETE /fapi/v1/order (signed)

        Args:
            symbol: Trading symbol, e.g. "BTCUSDT".
            order_id: The Binance-assigned order ID to cancel.
        """
        norm_symbol = validate_symbol(symbol)
        logger.info("Cancelling order symbol=%s, orderId=%s...", norm_symbol, order_id)
        return self.client.delete(
            "/fapi/v1/order",
            params={"symbol": norm_symbol, "orderId": order_id},
            signed=True,
        )

    # ------------------------------------------------------------------
    # Order placement (signed)
    # ------------------------------------------------------------------
    def place_order(self, order: OrderRequest) -> dict:
        """
        Place a new order (MARKET or LIMIT, BUY or SELL).

        Endpoint: POST /fapi/v1/order (signed)

        Args:
            order: A validated `OrderRequest`.

        Returns:
            The parsed JSON order response from Binance.
        """
        params: dict[str, Any] = {
            "symbol": order.symbol,
            "side": order.side,
            "type": order.order_type,
            "quantity": order.quantity,
        }

        if order.order_type == "LIMIT":
            params["price"] = order.price
            params["timeInForce"] = "GTC"  # Good-Til-Cancelled, standard default.

        logger.info(
            "Placing %s %s order: symbol=%s, qty=%s, price=%s",
            order.order_type,
            order.side,
            order.symbol,
            order.quantity,
            order.price,
        )

        return self.client.post("/fapi/v1/order", params=params, signed=True)

    def place_market_order(self, symbol: str, side: str, quantity: float | str) -> dict:
        """Convenience wrapper to place a MARKET order."""
        order = OrderRequest.from_raw(symbol, side, "MARKET", quantity)
        return self.place_order(order)

    def place_limit_order(
        self, symbol: str, side: str, quantity: float | str, price: float | str
    ) -> dict:
        """Convenience wrapper to place a LIMIT order."""
        order = OrderRequest.from_raw(symbol, side, "LIMIT", quantity, price)
        return self.place_order(order)
