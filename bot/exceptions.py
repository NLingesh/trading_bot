"""
Custom exception hierarchy for the trading bot.

All exceptions raised by this project inherit from `TradingBotError`,
allowing calling code to catch a single base exception if desired, or
more specific subclasses for finer-grained error handling.
"""


class TradingBotError(Exception):
    """Base exception for all trading bot errors."""


# ---------------------------------------------------------------------------
# Network / transport errors
# ---------------------------------------------------------------------------
class NetworkError(TradingBotError):
    """Raised when a network-level failure occurs (DNS, connection, etc.)."""


class ConnectionFailedError(NetworkError):
    """Raised when a connection to the Binance Testnet cannot be established."""


class TimeoutError_(NetworkError):
    """Raised when a request exceeds the configured timeout."""


# ---------------------------------------------------------------------------
# HTTP / API errors
# ---------------------------------------------------------------------------
class APIError(TradingBotError):
    """
    Raised when the Binance API returns an error response.

    Attributes:
        status_code: HTTP status code returned by the server.
        error_code: Binance-specific error code (from the JSON body), if any.
        message: Human-readable error message.
    """

    def __init__(self, status_code: int, error_code: int | None, message: str) -> None:
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        super().__init__(
            f"APIError(status_code={status_code}, error_code={error_code}, "
            f"message={message!r})"
        )


class AuthenticationError(APIError):
    """Raised when authentication with the API fails (e.g. bad API key)."""


class InvalidSignatureError(APIError):
    """Raised when the HMAC signature is rejected by Binance."""


class RateLimitError(APIError):
    """Raised when the API responds with a rate-limit related error (HTTP 429/418)."""


class ServerError(APIError):
    """Raised when the API responds with a 5xx server error."""


class JSONParsingError(TradingBotError):
    """Raised when a response body cannot be parsed as JSON."""


# ---------------------------------------------------------------------------
# Validation errors
# ---------------------------------------------------------------------------
class ValidationError(TradingBotError):
    """Base class for input validation errors."""


class InvalidSymbolError(ValidationError):
    """Raised when a trading symbol fails validation."""


class InvalidSideError(ValidationError):
    """Raised when an order side is not BUY or SELL."""


class InvalidOrderTypeError(ValidationError):
    """Raised when an order type is not MARKET or LIMIT."""


class InvalidQuantityError(ValidationError):
    """Raised when a quantity is missing, non-numeric, or non-positive."""


class InvalidPriceError(ValidationError):
    """Raised when a price is required (LIMIT orders) but missing/invalid."""


# ---------------------------------------------------------------------------
# Configuration errors
# ---------------------------------------------------------------------------
class ConfigurationError(TradingBotError):
    """Raised when required configuration (e.g. API keys) is missing or invalid."""
