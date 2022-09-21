from typing import Union
from dataclasses import dataclass
import re

__all__ = ["STEAM_CODE"]


@dataclass
class Regex:
    """Dataclass for a type of pattern"""
    pattern: str
    flags: Union[int, re.RegexFlag] = 0

    def is_in(self, text: str) -> bool:
        """Check if a match for a pattern can be found within a string"""
        return re.search(self.pattern, text, self.flags) is not None


STEAM_CODE = Regex(pattern="[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}", flags=re.IGNORECASE)
