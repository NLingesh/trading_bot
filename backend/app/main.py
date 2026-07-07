from __future__ import annotations
import logging, os
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.client import BinanceRestClient
from app.exceptions import BinanceAPIError, ConfigurationError, NetworkError, ValidationError
from app.logging_config import setup_logging
from app.models import LimitOrderRequest, MarketOrderRequest
from app.utils import require_env, format_order
from app.validators import validate_symbol, validate_quantity, validate_price
import app.orders as svc

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logging.getLogger("trading_bot").info("Trading bot started — Binance Futures Testnet")
    yield
    logging.getLogger("trading_bot").info("Shut down")

app = FastAPI(
    title="Binance Futures Testnet Trading Bot",
    description="Raw REST API trading bot — no SDK, no ccxt.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Exception handlers ────────────────────────────────────────────────────────
@app.exception_handler(BinanceAPIError)
async def _binance(req, exc: BinanceAPIError):
    h = {-2015: 401, -1022: 401, -1100: 422, -1121: 422}
    return JSONResponse(h.get(exc.code, 400), {"error": "Binance API Error", "code": exc.code, "message": exc.message})

@app.exception_handler(NetworkError)
async def _network(req, exc): return JSONResponse(503, {"error": "Network Error", "message": str(exc)})

@app.exception_handler(ValidationError)
async def _val(req, exc): return JSONResponse(422, {"error": "Validation Error", "message": str(exc)})

@app.exception_handler(ConfigurationError)
async def _cfg(req, exc): return JSONResponse(500, {"error": "Configuration Error", "message": str(exc)})

# ── Dependencies ──────────────────────────────────────────────────────────────
def get_client() -> BinanceRestClient:
    return BinanceRestClient(
        api_key=require_env("BINANCE_API_KEY"),
        api_secret=require_env("BINANCE_API_SECRET"),
        base_url=os.getenv("BINANCE_BASE_URL", "https://testnet.binancefuture.com"),
    )

def get_public_client() -> BinanceRestClient:
    return BinanceRestClient(
        api_key="", api_secret="",
        base_url=os.getenv("BINANCE_BASE_URL", "https://testnet.binancefuture.com"),
    )

# ── System ────────────────────────────────────────────────────────────────────
@app.get("/ping", tags=["System"])
def ping(c: BinanceRestClient = Depends(get_public_client)):
    return {"status": "ok", "binance": svc.ping(c)}

@app.get("/server-time", tags=["System"])
def server_time(c: BinanceRestClient = Depends(get_public_client)):
    return svc.server_time(c)

@app.get("/exchange-info", tags=["System"])
def exchange_info(symbol: Optional[str] = Query(None), c: BinanceRestClient = Depends(get_public_client)):
    return svc.exchange_info(c, symbol)

# ── Account ───────────────────────────────────────────────────────────────────
@app.get("/account", tags=["Account"])
def account(c: BinanceRestClient = Depends(get_client)):
    return svc.get_account(c)

@app.get("/positions", tags=["Account"])
def positions(symbol: Optional[str] = Query(None), c: BinanceRestClient = Depends(get_client)):
    return svc.get_positions(c, symbol)

# ── Orders ────────────────────────────────────────────────────────────────────
@app.get("/open-orders", tags=["Orders"])
def open_orders(symbol: Optional[str] = Query(None), c: BinanceRestClient = Depends(get_client)):
    return svc.get_open_orders(c, symbol)

@app.get("/order-status/{symbol}/{order_id}", tags=["Orders"])
def order_status(symbol: str, order_id: int, c: BinanceRestClient = Depends(get_client)):
    return svc.get_order_status(c, validate_symbol(symbol), order_id)

@app.post("/order/market", tags=["Orders"], status_code=201)
def market_order(order: MarketOrderRequest, c: BinanceRestClient = Depends(get_client)):
    validate_symbol(order.symbol); validate_quantity(order.quantity)
    return format_order(svc.place_market_order(c, order.symbol, order.side.value, order.quantity))

@app.post("/order/limit", tags=["Orders"], status_code=201)
def limit_order(order: LimitOrderRequest, c: BinanceRestClient = Depends(get_client)):
    validate_symbol(order.symbol); validate_quantity(order.quantity); validate_price(order.price)
    return format_order(svc.place_limit_order(c, order.symbol, order.side.value, order.quantity, order.price, order.time_in_force.value))

@app.delete("/cancel/{symbol}/{order_id}", tags=["Orders"])
def cancel(symbol: str, order_id: int, c: BinanceRestClient = Depends(get_client)):
    return format_order(svc.cancel_order(c, validate_symbol(symbol), order_id))
