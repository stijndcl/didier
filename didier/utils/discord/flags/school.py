from typing import Optional

from didier.data import constants
from didier.utils.discord.flags import PosixFlags

__all__ = ["StudyGuideFlags"]


class StudyGuideFlags(PosixFlags):
    """Flags for the study guide command"""

    year: Optional[int] = constants.CURRENT_YEAR
