import os
from app.exceptions import ConfigurationError

def require_env(key: str) -> str:
    v = os.getenv(key, "").strip()
    if not v:
        raise ConfigurationError(f"'{key}' is not set. Copy .env.example to .env.")
    return v

def format_order(raw: dict) -> dict:
    return {
        "order_id": raw.get("orderId"),
        "client_order_id": raw.get("clientOrderId"),
        "symbol": raw.get("symbol"),
        "status": raw.get("status"),
        "side": raw.get("side"),
        "type": raw.get("type"),
        "price": raw.get("price"),
        "orig_qty": raw.get("origQty"),
        "executed_qty": raw.get("executedQty"),
        "avg_price": raw.get("avgPrice"),
        "time_in_force": raw.get("timeInForce"),
        "update_time": raw.get("updateTime"),
        "raw": raw,
    }
