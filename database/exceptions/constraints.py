__all__ = ["DuplicateInsertException", "ForbiddenNameException"]


class DuplicateInsertException(Exception):
    """Exception raised when a value already exists"""


class ForbiddenNameException(Exception):
    """Exception raised when trying to insert something with a name that isn't allowed"""
