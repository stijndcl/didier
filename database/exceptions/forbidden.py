__all__ = ["Forbidden"]


class Forbidden(Exception):
    """Exception raised when trying to access a resource that isn't yours"""
