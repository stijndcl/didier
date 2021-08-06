import dacite
from dacite import from_dict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enums.platform import Platform, get_platform
from functions.config import get
from functions.timeFormatters import fromArray, forward_to_weekday, intToWeekday
import json
from typing import Dict, Optional, List


@dataclass
class Holiday:
    start_date: List[int]
    end_date: List[int]
    start_date_parsed: datetime = field(init=False)
    end_date_parsed: datetime = field(init=False)
    duration: timedelta = field(init=False)

    def __post_init__(self):
        self.start_date_parsed = fromArray(self.start_date)
        self.end_date_parsed = fromArray(self.end_date)
        self.duration = self.end_date_parsed - self.start_date_parsed

    def has_passed(self, current_day: datetime) -> bool:
        """
        Check if a holiday has passed already
        """
        return current_day > self.end_date_parsed


@dataclass
class Course:
    name: str


@dataclass
class Location:
    campus: str
    building: str
    room: str


@dataclass
class Timeslot:
    course: Course
    start_time: int
    end_time: int
    canceled: bool = False
    is_special: bool = False
    location: Optional[Location] = None
    online_link: Optional[str] = None
    online_platform: Optional[Platform] = None

    @staticmethod
    def from_slot_dict(slot_dict: Dict, course_dict: Dict, current_week: int):
        """
        Construct a Timeslot from a dict of data
        """
        if "weeks" in slot_dict and str(current_week) in slot_dict["weeks"]:
            return Timeslot.special_from_dict(slot_dict, course_dict, str(current_week))

        course = Course(course_dict["course"])
        start_time = slot_dict["time"]["start"]
        end_time = slot_dict["time"]["end"]

        # Location can be none if a class is online-only
        location = dacite.from_dict(Location, slot_dict["location"]) if "location" in slot_dict else None

        # Find platform & link if this class is online
        online_platform: Platform = get_platform(slot_dict.get("online", None))
        online_link = course_dict["online_links"][Platform.value["rep"]] if online_platform is not None else None

        return Timeslot(course=course, start_time=start_time, end_time=end_time, canceled=False, is_special=False,
                        location=location, online_platform=online_platform, online_link=online_link)

    @staticmethod
    def special_from_dict(slot_dict: Dict, course_dict: Dict, current_week: str):
        """
        Create a SPECIAL Timeslot from a dict and data
        """
        course = Course(course_dict["course"])
        # TODO

@dataclass
class Schedule:
    day: datetime
    targetted_weekday: bool = False
    schedule_dict: Dict = field(init=False)
    start_date: datetime = field(init=False)
    end_date: datetime = field(init=False)
    semester_over: bool = False
    holiday_offset: int = 0
    current_holiday: Optional[Holiday] = None
    _weekday_str: str = field(init=False)

    def __post_init__(self):
        self.schedule_dict: Dict = self.load_schedule_file()
        self.start_date = fromArray(self.schedule_dict["semester_start"])
        self.end_date = fromArray(self.schedule_dict["semester_end"])

        # Semester is over
        if self.end_date <= self.day:
            self.semester_over = True
            return

        self.check_holidays()

        # TODO show a custom embed when no class instead of fast-forwarding
        # # Store the target weekday (in case it exists) so we can ask for the next
        # # friday after the holiday, for example
        # target_weekday = -1 if not self.targetted_weekday else self.day.weekday()
        #
        # # Show schedule for after holidays
        # if self.current_holiday is not None:
        #     # Set day to day after holiday
        #     self.day = self.current_holiday.end_date_parsed + timedelta(days=1)
        #
        # # Find the next [DAY] after the holidays
        # if target_weekday != -1:
        #     self.day = forward_to_weekday(self.day, target_weekday)

        self._weekday_str = intToWeekday(self.day.weekday())

        print(self.day)

    def check_holidays(self):
        """
        Do all holiday-related stuff here to avoid multiple loops
        """
        for hol_entry in self.schedule_dict.get("holidays", []):
            holiday: Holiday = from_dict(Holiday, hol_entry)

            # Hasn't happened yet, don't care
            if holiday.start_date_parsed > self.day:
                continue

            # In the past: add the offset
            if holiday.has_passed(self.day):
                self.holiday_offset += (self.day - holiday.end_date_parsed) // 7
            elif holiday.start_date_parsed <= self.day <= holiday.end_date_parsed:
                self.current_holiday = holiday

    def load_schedule_file(self) -> Dict:
        """
        Load the schedule from the JSON file
        """
        semester = get_platform("semester")
        year = get_platform("year")

        with open(f"files/schedules/{year}{semester}.json", "r") as fp:
            return json.load(fp)

    def get_week(self) -> int:
        """
        Get the current week of the semester
        """
        diff: timedelta = self.day - self.start_date

        # Hasn't started yet, show week 1
        if diff.days < 0:
            return 1

        # Add +1 at the end because week 1 would be 0 as it's not over yet
        return (diff.days // 7) + self.holiday_offset + 1

    def find_slots_for_course(self, course_dict: Dict, current_week: int) -> List[Timeslot]:
        """
        Create time timeslots for a course
        """
        slots_today = []

        # First create a list of all slots of today
        for slot in course_dict["slots"]:
            # This slot is for a different day
            if slot["time"]["day"] != self._weekday_str.lower():
                continue

            slots_today.append(slot)

        # Create Timeslots
        slots_today = list(map(lambda x: Timeslot.from_slot_dict(x, course_dict, current_week), slots_today))

        return slots_today

    def create_schedule(self):
        """
        Create the schedule for the current week
        """
        week: int = self.get_week()
        slots: List[List[Timeslot]] = [self.find_slots_for_course(course, week) for course in self.schedule_dict["schedule"]]
        slots_flattened = [item for sublist in slots for item in sublist]
