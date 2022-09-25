__all__ = ["HTTPException"]


class HTTPException(RuntimeError):
    """Error raised when an API call fails"""

    def __init__(self, status_code: int):
        super().__init__(f"Something went wrong (status {status_code}).")
