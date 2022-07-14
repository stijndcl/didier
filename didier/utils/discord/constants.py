from enum import Enum

__all__ = ["Limits"]


class Limits(int, Enum):
    """Enum for the limits of certain fields"""

    EMBED_AUTHOR_LENGTH = 256
    EMBED_DESCRIPTION_LENGTH = 4096
    EMBED_FIELD_COUNT = 25
    EMBED_FIELD_NAME_LENGTH = 256
    EMBED_FIELD_VALUE_LENGTH = 1024
    EMBED_FOOTER_LENGTH = 2048
    EMBED_TITLE_LENGTH = 256
    EMBED_TOTAL_LENGTH = 6000
    MESSAGE_LENGTH = 2000
