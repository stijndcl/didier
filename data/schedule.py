from abc import ABC, abstractmethod
from dacite import from_dict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from discord import Colour, Embed
from enums.platform import Platform, get_platform
from functions.timeFormatters import fromArray, intToWeekday, timeFromInt
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

    def __str__(self):
        return self.name


@dataclass
class Location:
    campus: str
    building: str
    room: str

    def __str__(self):
        return f"{self.campus} {self.building} {self.room}"


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

    def __str__(self):
        time_str = f"{timeFromInt(self.start_time)} - {timeFromInt(self.end_time)}"

        return f"{time_str}: {self.course} {self._get_location_str()}"

    def get_link_str(self) -> Optional[str]:
        if self.online_link is None or self.online_platform is None:
            return None

        return f"[{self.online_platform.value.get('name')}]({self.online_link})"

    def _get_location_str(self, offline_prefix="in", online_prefix="**online** @") -> str:
        return f"{offline_prefix} {self.location}" if self.location is not None \
            else f"{online_prefix} **{self.get_link_str()}**"

    def get_special_fmt_str(self) -> Optional[str]:
        if not self.canceled and not self.is_special:
            return None

        # This class was canceled
        if self.canceled:
            return f"{self.course} van {timeFromInt(self.start_time)} gaat vandaag **niet** door."

        # Something else is wrong
        return f"{self.course} gaat vandaag door van **{timeFromInt(self.start_time)}** tot " \
               f"**{timeFromInt(self.end_time)}** {self._get_location_str(online_prefix='op')}"

    @staticmethod
    def from_slot_dict(slot_dict: Dict, course_dict: Dict, current_week: int):
        """
        Construct a Timeslot from a dict of data
        """
        special = False

        if "weeks" in slot_dict and str(current_week) in slot_dict["weeks"]:
            # If at least one thing was changed, this slot requires extra attention
            special = True
            # Overwrite the normal data with the customized entries
            slot_dict.update(slot_dict["weeks"][str(current_week)])

            # Only happens online, not on-campus
            online_only = slot_dict["weeks"][str(current_week)].get("online_only", False)
            if online_only:
                slot_dict.pop("location")

        course = Course(course_dict["course"])
        start_time = slot_dict["time"]["start"]
        end_time = slot_dict["time"]["end"]

        # Location can be none if a class is online-only
        location = from_dict(Location, slot_dict["location"]) if "location" in slot_dict else None

        # Find platform & link if this class is online
        online_platform: Platform = get_platform(slot_dict.get("online", None))

        # Custom online link for this day if it exists, else the general link for this platform
        online_link = \
            slot_dict["online_link"] if "online_link" in slot_dict else \
            course_dict["online_links"][online_platform.value["rep"]] \
            if online_platform is not None \
            else None

        return Timeslot(course=course, start_time=start_time, end_time=end_time, canceled="canceled" in slot_dict,
                        is_special=special, location=location, online_platform=online_platform, online_link=online_link)


@dataclass
class Schedule:
    day: datetime
    year: int
    semester: int
    targeted_weekday: bool = False
    week: int = field(init=False)
    schedule_dict: Dict = field(init=False)
    start_date: datetime = field(init=False)
    end_date: datetime = field(init=False)
    semester_over: bool = False
    holiday_offset: int = 0
    current_holiday: Optional[Holiday] = None
    weekday_str: str = field(init=False)

    def __post_init__(self):
        self.schedule_dict: Dict = self.load_schedule_file()
        self.start_date = fromArray(self.schedule_dict["semester_start"])
        self.end_date = fromArray(self.schedule_dict["semester_end"])
        self._forward_to_semester()

        # Semester is over
        if self.end_date < self.day:
            self.semester_over = True
            return

        self.check_holidays()
        self.week = self.get_week()

        # # Store the target weekday (in case it exists) so we can ask for the next
        # # friday after the holiday, for example
        # target_weekday = -1 if not self.targeted_weekday else self.day.weekday()
        #
        # # Show schedule for after holidays
        # if self.current_holiday is not None:
        #     # Set day to day after holiday
        #     self.day = self.current_holiday.end_date_parsed + timedelta(days=1)
        #
        # # Find the next [DAY] after the holidays
        # if target_weekday != -1:
        #     self.day = forward_to_weekday(self.day, target_weekday)

        self.weekday_str = intToWeekday(self.day.weekday())

    def _forward_to_semester(self):
        """
        In case the semester hasn't started yet, fast forward the current date
        by a week until it's no longer necessary
        """
        while self.day < self.start_date:
            self.day += timedelta(weeks=1)

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
                # Add 1 because Monday-Sunday is only 6 days, but should be counted as a week
                self.holiday_offset += (holiday.duration.days + 1) // 7
            elif holiday.start_date_parsed <= self.day <= holiday.end_date_parsed:
                self.current_holiday = holiday

    def load_schedule_file(self) -> Dict:
        """
        Load the schedule from the JSON file
        """
        with open(f"files/schedules/{self.year}{self.semester}.json", "r") as fp:
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
        # Every week would be one behind
        # Also subtract all passed holidays
        return (diff.days // 7) - self.holiday_offset + 1

    def find_slots_for_course(self, course_dict: Dict) -> List[Timeslot]:
        """
        Create time timeslots for a course
        """
        slots_today = []

        # First create a list of all slots of today
        for slot in course_dict["slots"]:
            # This slot is for a different day
            if slot["time"]["day"] != self.weekday_str.lower():
                continue

            slots_today.append(slot)

        # Create Timeslots
        slots_today = list(map(lambda x: Timeslot.from_slot_dict(x, course_dict, self.week), slots_today))

        return slots_today

    def create_schedule(self):
        """
        Create the schedule for the current week
        """
        if self.current_holiday is not None:
            return HolidayEmbed(self)

        slots: List[List[Timeslot]] = [self.find_slots_for_course(course) for course in self.schedule_dict["schedule"]]
        minor_slots = {}

        # Find minor slots
        for minor in self.schedule_dict["minors"]:
            m_slots = []
            for course in minor["schedule"]:
                # Go over every course
                m_slots.append(self.find_slots_for_course(course))

            # Flatten list
            m_slots = [item for sublist in m_slots for item in sublist]
            # Sort by timestamp
            m_slots.sort(key=lambda x: x.start_time)

            minor_slots[minor["name"]] = m_slots

        slots_flattened = [item for sublist in slots for item in sublist]

        # Sort by timestamp
        slots_flattened.sort(key=lambda x: x.start_time)
        not_canceled = list(filter(lambda x: not x.canceled, slots_flattened))

        # All classes are canceled
        if not not_canceled:
            return NoClassEmbed(self, slots_flattened)

        return ScheduleEmbed(self, slots_flattened, not_canceled, minor_slots)


@dataclass
class LesEmbed(ABC):
    """
    Abstract base class for Les embeds
    """
    schedule: Schedule

    def get_author(self) -> str:
        level = "Bachelor" if self.schedule.year < 4 else "Master"
        year = self.schedule.year if self.schedule.year < 4 else self.schedule.year - 3
        suffix = "ste" if self.schedule.year == 1 else "de"
        return f"Lessenrooster voor {year}{suffix} {level}"

    def get_title(self) -> str:
        date = self.schedule.day.strftime("%d/%m/%Y")
        return f"{self.schedule.weekday_str} {date}"

    def get_footer(self) -> str:
        return f"Semester {self.schedule.semester} | Lesweek {self.schedule.week}"

    def get_extras(self) -> str:
        return ""

    def add_minors(self, embed: Embed):
        pass

    def get_online_links(self) -> str:
        return ""

    @abstractmethod
    def get_description(self) -> str:
        pass

    def to_embed(self) -> Embed:
        embed = Embed(title=self.get_title(), colour=Colour.blue())
        embed.set_author(name=self.get_author())
        embed.set_footer(text=self.get_footer())

        embed.description = self.get_description()

        # Add links if there are any
        links = self.get_online_links()
        if links:
            embed.add_field(name="Online links", value=links, inline=False)

        self.add_minors(embed)

        # Add extras if there are any
        extras = self.get_extras()
        if extras:
            embed.add_field(name="Extra", value=extras, inline=False)

        return embed


@dataclass
class HolidayEmbed(LesEmbed):
    """
    Class for a Les embed sent during holidays
    """
    def get_description(self) -> str:
        date = self.schedule.current_holiday.end_date_parsed.strftime("%d/%m/%Y")
        return f"Het is momenteel **vakantie** tot en met **{date}**."


@dataclass
class NoClassEmbed(LesEmbed):
    """
    Class for a Les embed when all classes are canceled or there are none at all
    """
    slots: List[Timeslot]

    def get_description(self) -> str:
        return "Geen les"

    def get_extras(self) -> str:
        canceled = list(filter(lambda x: x.canceled, self.slots))
        if not canceled:
            return ""

        return "\n".join(list(entry.get_special_fmt_str() for entry in canceled))


@dataclass
class ScheduleEmbed(LesEmbed):
    """
    Class for a successful schedule
    """
    slots: List[Timeslot]
    slots_not_canceled: List[Timeslot]
    minor_slots: Dict[str, List[Timeslot]]

    def get_description(self) -> str:
        return "\n".join(list(f"{entry}" for entry in self.slots_not_canceled))

    def add_minors(self, embed: Embed):
        for minor, slots in self.minor_slots.items():
            if not slots:
                continue

            not_canceled = list(filter(lambda x: not x.canceled, slots))
            info = "\n".join(list(str(entry) for entry in not_canceled))

            special = list(filter(lambda x: x.is_special or x.canceled, slots))

            # Add extra info about this minor
            if special:
                info += "\n" + "\n".join(list(entry.get_special_fmt_str() for entry in special))

            embed.add_field(name=f"Minor {minor}", value=info, inline=False)

    def get_extras(self) -> str:
        special = list(filter(lambda x: x.is_special or x.canceled, self.slots))

        if not special:
            return ""

        return "\n".join(list(entry.get_special_fmt_str() for entry in special))

    def get_online_links(self) -> str:
        has_link = list(filter(lambda x: x.online_link is not None, self.slots))

        if not has_link:
            return ""

        return "\n".join(list(f"{entry.course}: **{entry.get_link_str()}**" for entry in has_link))
