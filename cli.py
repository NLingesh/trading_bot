#!/usr/bin/env python3
"""
Command-line interface for the Binance Futures Testnet trading bot.

Examples:
    python cli.py --symbol BTCUSDT --side BUY --type MARKET --qty 0.01
    python cli.py --symbol BTCUSDT --side SELL --type LIMIT --qty 0.01 --price 110000
    python cli.py --info account
    python cli.py --info positions --symbol BTCUSDT
    python cli.py --info open-orders --symbol BTCUSDT
    python cli.py --info order-status --symbol BTCUSDT --order-id 12345678
    python cli.py --cancel --symbol BTCUSDT --order-id 12345678
"""

from __future__ import annotations

import argparse
import sys

from dotenv import load_dotenv

from bot.client import RestClient
from bot.exceptions import TradingBotError
from bot.logging_config import get_logger, setup_logging
from bot.orders import BinanceFuturesEndpoints, OrderRequest
from bot.utils import format_order_summary, require_env

BASE_URL = "https://testnet.binancefuture.com"


def build_arg_parser() -> argparse.ArgumentParser:
    """Construct the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="cli.py",
        description="Binance Futures Testnet Trading Bot (raw REST API, no SDKs).",
    )

    parser.add_argument("--symbol", type=str, help="Trading symbol, e.g. BTCUSDT")
    parser.add_argument("--side", type=str, choices=["BUY", "SELL"], help="Order side")
    parser.add_argument(
        "--type", type=str, choices=["MARKET", "LIMIT"], dest="order_type", help="Order type"
    )
    parser.add_argument("--qty", type=str, help="Order quantity, e.g. 0.01")
    parser.add_argument("--price", type=str, help="Order price (required for LIMIT orders)")

    parser.add_argument("--order-id", type=int, help="Order ID (for status/cancel operations)")

    parser.add_argument(
        "--info",
        type=str,
        choices=["account", "positions", "open-orders", "order-status", "ping", "time", "exchange-info"],
        help="Fetch informational data instead of placing an order.",
    )
    parser.add_argument(
        "--cancel", action="store_true", help="Cancel the order identified by --symbol/--order-id."
    )

    return parser


def print_success(message: str) -> None:
    """Print a clearly-marked success message."""
    print(f"\n✅ SUCCESS: {message}\n")


def print_failure(message: str) -> None:
    """Print a clearly-marked failure message."""
    print(f"\n❌ FAILURE: {message}\n", file=sys.stderr)


def run(args: argparse.Namespace) -> int:
    """
    Execute the requested action based on parsed CLI arguments.

    Returns:
        Process exit code (0 for success, 1 for failure).
    """
    logger = get_logger()

    try:
        api_key = require_env("BINANCE_API_KEY")
        api_secret = require_env("BINANCE_API_SECRET")
    except TradingBotError as exc:
        print_failure(str(exc))
        return 1

    client = RestClient(api_key=api_key, api_secret=api_secret, base_url=BASE_URL)
    endpoints = BinanceFuturesEndpoints(client)

    try:
        # ---------------- Informational actions ----------------
        if args.info == "ping":
            result = endpoints.ping()
            print("Ping OK:", result)
            print_success("Connectivity check passed.")
            return 0

        if args.info == "time":
            result = endpoints.get_server_time()
            print("Server time:", result)
            print_success("Fetched server time.")
            return 0

        if args.info == "exchange-info":
            result = endpoints.get_exchange_info()
            symbols = result.get("symbols", [])
            print(f"Exchange info: {len(symbols)} symbols available.")
            print_success("Fetched exchange information.")
            return 0

        if args.info == "account":
            result = endpoints.get_account_info()
            print("Account info:")
            print(f"  Total Wallet Balance : {result.get('totalWalletBalance')}")
            print(f"  Total Unrealized PnL : {result.get('totalUnrealizedProfit')}")
            print(f"  Available Balance    : {result.get('availableBalance')}")
            print_success("Fetched account information.")
            return 0

        if args.info == "positions":
            result = endpoints.get_position_info(symbol=args.symbol)
            print(f"Positions ({len(result)}):")
            for pos in result:
                amt = float(pos.get("positionAmt", 0))
                if amt != 0:
                    print(f"  {pos.get('symbol')}: amt={amt}, entryPrice={pos.get('entryPrice')}")
            print_success("Fetched position information.")
            return 0

        if args.info == "open-orders":
            result = endpoints.get_open_orders(symbol=args.symbol)
            print(f"Open orders ({len(result)}):")
            for order in result:
                print(f"  {order.get('symbol')} | orderId={order.get('orderId')} | "
                      f"{order.get('side')} {order.get('type')} qty={order.get('origQty')}")
            print_success("Fetched open orders.")
            return 0

        if args.info == "order-status":
            if not args.symbol or not args.order_id:
                print_failure("--symbol and --order-id are required for order-status.")
                return 1
            result = endpoints.get_order_status(args.symbol, args.order_id)
            print(format_order_summary(result))
            print_success("Fetched order status.")
            return 0

        # ---------------- Cancel action ----------------
        if args.cancel:
            if not args.symbol or not args.order_id:
                print_failure("--symbol and --order-id are required to cancel an order.")
                return 1
            result = endpoints.cancel_order(args.symbol, args.order_id)
            print(format_order_summary(result))
            print_success(f"Order {args.order_id} cancelled.")
            return 0

        # ---------------- Place order ----------------
        if not (args.symbol and args.side and args.order_type and args.qty):
            print_failure(
                "To place an order, --symbol, --side, --type, and --qty are required "
                "(and --price for LIMIT orders)."
            )
            return 1

        order = OrderRequest.from_raw(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.qty,
            price=args.price,
        )
        result = endpoints.place_order(order)
        print(format_order_summary(result))
        print_success(f"{order.order_type} {order.side} order placed for {order.symbol}.")
        return 0

    except TradingBotError as exc:
        logger.error("Operation failed: %s", exc)
        print_failure(str(exc))
        return 1
    except Exception as exc:  # noqa: BLE001 - final safety net for unexpected errors
        logger.exception("Unexpected error occurred.")
        print_failure(f"Unexpected error: {exc}")
        return 1


def main() -> None:
    """CLI entry point."""
    load_dotenv()
    setup_logging()

    parser = build_arg_parser()
    args = parser.parse_args()

    exit_code = run(args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
