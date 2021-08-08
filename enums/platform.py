from enum import Enum
from typing import Optional


class Platform(Enum):
    """
    An Enum to represent online class platforms
    Name: The name of the platform
    Rep: A shorter, lowercased & space-less version
    """
    BongoVC = {"name": "Bongo Virtual Classroom", "rep": "bongo"}
    GatherTown = {"name": "Gather Town", "rep": "gather"}
    MSTeams = {"name": "MS Teams", "rep": "msteams"}
    OpenCast = {"name": "OpenCast", "rep": "opencast"}
    Ufora = {"name": "Ufora", "rep": "ufora"}
    Zoom = {"name": "Zoom", "rep": "zoom"}


def get_platform(rep: Optional[str]) -> Optional[Platform]:
    """
    Find the platform that corresponds to the given name
    """
    if rep is None:
        return None

    for platform in Platform:
        if platform.value["rep"] == rep:
            return platform

    return None
