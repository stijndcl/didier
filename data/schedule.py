import json
from dacite import from_dict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enums.platforms import Platforms
from functions.config import get
from typing import Dict, Optional, List

from functions.timeFormatters import fromArray


@dataclass
class Holiday:
    start_list: List[int]
    end_list: List[int]
    start_date: datetime = field(init=False)
    end_date: datetime = field(init=False)
    duration: timedelta = field(init=False)

    def __post_init__(self):
        self.start_date = fromArray(self.start_list)
        self.end_date = fromArray(self.end_list)
        self.duration = self.end_date - self.start_date

    def has_passed(self, current_day: datetime) -> bool:
        """
        Check if a holiday has passed already
        """
        return current_day > self.end_date


@dataclass
class Course:
    day: str
    week: int
    course_dict: Dict


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
    online_platform: Optional[Platforms] = None


@dataclass
class Schedule:
    day: datetime
    schedule_dict: Dict = field(init=False)
    start_date: datetime
    end_date: datetime
    semester_over: bool = False
    holiday_offset: int = 0
    current_holiday: Optional[Holiday] = None

    def __post_init__(self):
        self.schedule_dict: Dict = self.load_schedule_file()
        self.start_date = fromArray(self.schedule_dict["semester_start"])
        self.end_date = fromArray(self.schedule_dict["semester_end"])

        # Semester is over
        if self.end_date <= self.day:
            self.semester_over = True
            return

        self.check_holidays()

        # Show schedule for after holidays
        if self.current_holiday is not None:
            self.day = self.current_holiday.end_date + timedelta(days=1)

    def check_holidays(self):
        """
        Do all holiday-related stuff here to avoid multiple loops
        """
        for hol_entry in self.schedule_dict.get("holidays", []):
            holiday: Holiday = from_dict(Holiday, hol_entry)

            # Hasn't happened yet, don't care
            if holiday.start_date > self.day:
                continue

            # In the past: add the offset
            if holiday.has_passed(self.day):
                self.holiday_offset += (self.day - holiday.end_date) // 7
            elif holiday.start_date <= self.day <= holiday.end_date:
                self.current_holiday = holiday

    def load_schedule_file(self) -> Dict:
        """
        Load the schedule from the JSON file
        """
        semester = get("semester")
        year = get("year")

        with open(f"files/{year}{semester}.json", "r") as fp:
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

    def create_schedule(self):
        """
        Create the schedule for the current week
        """
        week: int = self.get_week()
