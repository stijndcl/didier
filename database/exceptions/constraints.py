__all__ = ["DuplicateInsertException"]


class DuplicateInsertException(Exception):
    """Exception raised when a value already exists"""
