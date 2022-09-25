from enum import Enum

__all__ = ["EMOJI_MAP", "Limits"]


EMOJI_MAP = {
    "a": "🇦",
    "b": "🇧",
    "c": "🇨",
    "d": "🇩",
    "e": "🇪",
    "f": "🇫",
    "g": "🇬",
    "h": "🇭",
    "i": "🇮",
    "j": "🇯",
    "k": "🇰",
    "l": "🇱",
    "m": "🇲",
    "n": "🇳",
    "o": "🇴",
    "p": "🇵",
    "q": "🇶",
    "r": "🇷",
    "s": "🇸",
    "t": "🇹",
    "u": "🇺",
    "v": "🇻",
    "w": "🇼",
    "x": "🇽",
    "y": "🇾",
    "z": "🇿",
    "0": "0⃣",
    "1": "1️⃣",
    "2": "2️⃣",
    "3": "3️⃣",
    "4": "4️⃣",
    "5": "5️⃣",
    "6": "6️⃣",
    "7": "7️⃣",
    "8": "8️⃣",
    "9": "9️⃣",
}


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
