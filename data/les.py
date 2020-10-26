from enums.platforms import Platforms
from functions.timeFormatters import timeFromInt


# A container class for schedules
class Schedule:
    def __init__(self, schedule: dict):
        self.courses = [Course(course) for course in schedule]
        self.customs = []  # Courses that only the person that called the schedule has
        self.extra = []  # Courses that need special attention (canceled, online, ...)

    def addCustom(self, course):
        """
        Function that adds a course into the list of courses,
        useful for adding a user's custom courses
        """
        self.customs.append(Course(course))


# A container class for courses
class Course:
    # Initialize a course from the dict that the JSON contains
    def __init__(self, courseInfo: dict):
        self.courseInfo = courseInfo
        self.name = courseInfo["course"]

        self.slots = []
        self.initSlots()

        self.platforms = {}
        self.initPlatforms()

    def initSlots(self):
        """
        Function that creates Slot instances & adds them to the list
        """
        for slot in self.courseInfo["slots"]:
            self.slots.append(Slot(self, slot))

    def initPlatforms(self):
        """
        Function that creates Platform instances & adds them into the dict
        """
        for platform in Platforms:
            if platform["rep"] in self.courseInfo:
                self.platforms[platform["rep"]] = Platform(platform["name"], self.courseInfo[platform["rep"]])

    def getSlotsOnDay(self, day: str, week: int):
        """
        Function that returns a list of all slots of this course
        on a given day of the week

        This list then has duplicate days filtered out depending on
        whether or not there is a special class on this day
        """
        slots = []
        specials = []

        for slot in self.slots:
            # Skip slots on other days
            if slot.day != day:
                continue

            # TODO check weeks & filter slots down

            if slot.special:
                specials.append(slot)
            else:
                slots.append(slot)



# TODO add an is_online field to the JSON to allow toggling
#   temporary online classes easier
# A slot in a course
class Slot:
    def __init__(self, course: Course, slot: dict):
        self.course = course
        self.day = slot["time"][0]
        self.start = timeFromInt(slot["time"][1])
        self.end = timeFromInt(slot["time"][2])
        self.canceled = "canceled" in slot  # Boolean indicating whether or not this class has been canceled
        self.special = "weeks" in slot or self.canceled  # Boolean indicating if this class is special or generic

        # TODO check if on-campus, else None
        self.locations = self.setLocations(slot)
        self.platform = self.course.platforms[slot["online"]]

    def setLocations(self, slot: dict):
        """
        Function that creates a list of Location instances
        """
        locations = []

        # Slot has multiple locations
        if "locations" in slot:
            for location in slot["locations"]:
                locations.append(Location(location))
        else:
            # Slot has only one location
            locations.append(Location(slot))

        return locations

    def getLocations(self):
        """
        Function that creates a string representation for this
        slot's locations
        """
        if self.locations is None:
            return ""

    def getOnline(self):
        pass


# A location where a course might take place
class Location:
    def __init__(self, slot: dict):
        self.campus = slot["campus"]
        self.building = slot["building"]
        self.room = slot["room"]

    def __str__(self):
        return " ".join([self.campus, self.building, self.room])


# A streaming platform
class Platform:
    def __init__(self, name, url):
        self.name = name
        self.url = url
