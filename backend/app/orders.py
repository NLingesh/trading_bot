from typing import Any, Dict, Optional
from app.client import BinanceRestClient

FAPI_ORDER        = "/fapi/v1/order"
FAPI_OPEN_ORDERS  = "/fapi/v1/openOrders"
FAPI_ACCOUNT      = "/fapi/v2/account"
FAPI_POSITION     = "/fapi/v2/positionRisk"
FAPI_EXCHANGE     = "/fapi/v1/exchangeInfo"
FAPI_PING         = "/fapi/v1/ping"
FAPI_TIME         = "/fapi/v1/time"

def ping(c): return c.get(FAPI_PING)
def server_time(c): return c.get(FAPI_TIME)
def exchange_info(c, symbol=None):
    p = {"symbol": symbol.upper()} if symbol else {}
    return c.get(FAPI_EXCHANGE, params=p)

def get_account(c): return c.get(FAPI_ACCOUNT, signed=True)
def get_positions(c, symbol=None):
    p = {"symbol": symbol.upper()} if symbol else {}
    return c.get(FAPI_POSITION, params=p, signed=True)

def get_open_orders(c, symbol=None):
    p = {"symbol": symbol.upper()} if symbol else {}
    return c.get(FAPI_OPEN_ORDERS, params=p, signed=True)

def get_order_status(c, symbol: str, order_id: int):
    return c.get(FAPI_ORDER, params={"symbol": symbol.upper(), "orderId": order_id}, signed=True)

def place_market_order(c, symbol: str, side: str, quantity: float):
    return c.post(FAPI_ORDER, params={"symbol": symbol.upper(), "side": side.upper(), "type": "MARKET", "quantity": quantity})

def place_limit_order(c, symbol: str, side: str, quantity: float, price: float, time_in_force: str = "GTC"):
    return c.post(FAPI_ORDER, params={"symbol": symbol.upper(), "side": side.upper(), "type": "LIMIT", "quantity": quantity, "price": price, "timeInForce": time_in_force.upper()})

def cancel_order(c, symbol: str, order_id: int):
    return c.delete(FAPI_ORDER, params={"symbol": symbol.upper(), "orderId": order_id})
