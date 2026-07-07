import re
from app.exceptions import ValidationError

_SYMBOL_RE = re.compile(r"^[A-Z0-9]{2,20}$")

def validate_symbol(symbol: str) -> str:
    s = symbol.upper().strip()
    if not _SYMBOL_RE.match(s):
        raise ValidationError(f"Invalid symbol '{symbol}'. Use uppercase alphanumeric (e.g. BTCUSDT).")
    return s

def validate_quantity(qty: float) -> float:
    if qty <= 0:
        raise ValidationError("Quantity must be > 0.")
    return qty

def validate_price(price: float) -> float:
    if price <= 0:
        raise ValidationError("Price must be > 0.")
    return price
