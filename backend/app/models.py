from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, field_validator

class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class TimeInForce(str, Enum):
    GTC = "GTC"
    IOC = "IOC"
    FOK = "FOK"

class MarketOrderRequest(BaseModel):
    symbol: str = Field(..., examples=["BTCUSDT"])
    side: OrderSide
    quantity: float = Field(..., gt=0, examples=[0.001])

    @field_validator("symbol", mode="before")
    @classmethod
    def upper(cls, v): return v.upper().strip()

    model_config = {"json_schema_extra": {"example": {"symbol": "BTCUSDT", "side": "BUY", "quantity": 0.001}}}

class LimitOrderRequest(BaseModel):
    symbol: str = Field(..., examples=["BTCUSDT"])
    side: OrderSide
    quantity: float = Field(..., gt=0, examples=[0.001])
    price: float = Field(..., gt=0, examples=[50000.0])
    time_in_force: TimeInForce = TimeInForce.GTC

    @field_validator("symbol", mode="before")
    @classmethod
    def upper(cls, v): return v.upper().strip()

    model_config = {"json_schema_extra": {"example": {"symbol": "BTCUSDT", "side": "BUY", "quantity": 0.001, "price": 50000.0, "time_in_force": "GTC"}}}
