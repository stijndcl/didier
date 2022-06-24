from typing import Optional

from didier.data.flags import PosixFlags


class EditCustomFlags(PosixFlags):
    """Flags for the edit custom command"""

    name: Optional[str] = None
    response: Optional[str] = None
