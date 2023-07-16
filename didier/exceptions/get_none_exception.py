__all__ = ["GetNoneException"]


class GetNoneException(RuntimeError):
    """Exception raised when a Bot.get()-method returned None"""
