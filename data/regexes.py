import re

STEAM_CODE = {"pattern": "[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}", "flags": re.IGNORECASE}


def contains(text: str, pattern: dict) -> bool:
    if "flags" in pattern:
        return re.search(pattern["pattern"], text, pattern["flags"]) is not None
    else:
        return re.search(pattern["pattern"], text) is not None
