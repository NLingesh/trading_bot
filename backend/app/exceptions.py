class TradingBotError(Exception):
    pass

class BinanceAPIError(TradingBotError):
    def __init__(self, code: int, message: str, http_status: int = 400):
        self.code = code
        self.message = message
        self.http_status = http_status
        super().__init__(f"Binance API Error {code} (HTTP {http_status}): {message}")

class AuthenticationError(TradingBotError):
    pass

class NetworkError(TradingBotError):
    pass

class ValidationError(TradingBotError):
    pass

class ConfigurationError(TradingBotError):
    pass
