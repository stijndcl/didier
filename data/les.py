from functions.timeFormatters import timeFromInt


# A container class for classes
class Course:
    # Initialize a course from the dict that the JSON contains
    def __init__(self, courseInfo: dict):
        self.name = courseInfo["course"]


# A slot in a course
class Slot:
    def __init__(self, slot: dict):
        self.day = slot["time"][0]
        self.start = timeFromInt(slot["time"][1])
        self.end = timeFromInt(slot["time"][2])
        self.locations = self.getLocations(slot)

    def getLocations(self, slot: dict):
        locations = []

        # Slot has multiple locations
        if "locations" in slot:
            for location in slot["locations"]:
                locations.append(Location(location))
        else:
            # Slot has only one location
            locations.append(Location(slot))

        return locations


# A location where a course might take place
class Location:
    def __init__(self, slot: dict):
        self.campus = slot["campus"]
        self.building = slot["building"]
        self.room = slot["room"]


# A streaming platform
class Platform:
    pass
