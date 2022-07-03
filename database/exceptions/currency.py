class DoubleNightly(Exception):
    """Exception raised when claiming nightlies multiple times per day"""


class NotEnoughDinks(Exception):
    """Exception raised when trying to do something you don't have the Dinks for"""
