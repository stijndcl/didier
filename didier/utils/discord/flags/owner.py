from typing import Optional

from discord.ext import commands

from didier.utils.discord.flags import PosixFlags

__all__ = ["EditCustomFlags", "SyncOptionFlags"]


class EditCustomFlags(PosixFlags):
    """Flags for the edit custom command"""

    name: Optional[str] = None
    response: Optional[str] = None


class SyncOptionFlags(PosixFlags):
    """Flags for the sync command"""

    clear: bool = False
    copy_globals: bool = commands.flag(aliases=["copy_global", "copy"], default=False)
