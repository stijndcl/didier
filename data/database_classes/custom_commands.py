from attr import dataclass


@dataclass
class CustomCommand:
    """
    Class to store custom commands being triggered
    """
    id: int = None
    name: str = None
    response: str = None
    alias_used: str = None

    def __nonzero__(self):
        return self.id is not None
