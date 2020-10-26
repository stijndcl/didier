from enum import Enum


class Platforms(Enum):
    """
    An Enum to represent online class platforms
    Name: The name of the platform
    Rep: A shorter, lowercased & space-less version
    """
    Bongo = {"name": "Bongo Virtual Classroom", "rep": "bongo"}
    MSTeams = {"name": "MS Teams", "rep": "msteams"}
    Ufora = {"name": "Ufora", "rep": "ufora"}
    Zoom = {"name": "Zoom", "rep": "zoom"}
