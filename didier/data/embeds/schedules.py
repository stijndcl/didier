from __future__ import annotations

import pathlib
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from didier import Didier

import discord
from ics import Calendar
from overrides import overrides
from sqlalchemy.ext.asyncio import AsyncSession

from database.crud.ufora_courses import get_course_by_code
from database.schemas import UforaCourse
from didier.data.embeds.base import EmbedBaseModel
from didier.utils.discord import colours
from didier.utils.types.datetime import (
    LOCAL_TIMEZONE,
    int_to_weekday,
    time_string,
    tz_aware_today,
)
from didier.utils.types.string import leading
from settings import ScheduleType

__all__ = ["Schedule", "get_schedule_for_day", "parse_schedule_from_content", "parse_schedule"]


@dataclass
class Schedule(EmbedBaseModel):
    """An entire schedule"""

    slots: set[ScheduleSlot] = field(default_factory=set)

    def __add__(self, other) -> Schedule:
        """Combine schedules using the + operator"""
        if not isinstance(other, Schedule):
            raise TypeError("Argument to __add__ must be a Schedule")

        return Schedule(slots=self.slots.union(other.slots))

    def __bool__(self) -> bool:
        """Make empty schedules falsy"""
        return bool(self.slots)

    def on_day(self, day: date) -> Schedule:
        """Only show courses on a given day"""
        return Schedule(set(filter(lambda slot: slot.start_time.date() == day, self.slots)))

    def personalize(self, roles: set[int]) -> Schedule:
        """Personalize a schedule for a user, only adding courses they follow"""
        # If the schedule is already empty, just return instantly
        if not self.slots:
            return Schedule()

        personal_slots = []
        for slot in self.slots:
            alt_id = slot.alternative_overarching_role_id

            # Check if the user has a course selected in their roles
            role_found = slot.role_id is not None and slot.role_id in roles

            # Some engineering master courses are present in multiple different places,
            # so this is necessary
            overarching_role_found = (slot.overarching_role_id is not None and slot.overarching_role_id in roles) or (
                alt_id is not None and alt_id in roles
            )
            if role_found or overarching_role_found:
                personal_slots.append(slot)

        return Schedule(set(personal_slots))

    @overrides
    def to_embed(self, **kwargs) -> discord.Embed:
        day: date = kwargs.get("day", tz_aware_today())
        day_str = f"{leading('0', str(day.day))}/{leading('0', str(day.month))}/{leading('0', str(day.year))}"

        embed = discord.Embed(title=f"Schedule - {int_to_weekday(day.weekday())} {day_str}")

        if self:
            embed.colour = colours.ghent_university_blue()
        else:
            embed.colour = colours.error_red()
            embed.description = (
                "No planned classes found.\n\n"
                "In case this doesn't seem right, "
                "make sure that you've got the roles of all the courses that you're taking on.\n\n"
                "In case it does, enjoy your day off!"
            )

            return embed

        slots_sorted = sorted(list(self.slots), key=lambda k: k.start_time)
        description_data = []

        for slot in slots_sorted:
            description_data.append(
                f"{time_string(slot.start_time)} - {time_string(slot.end_time)}: {slot.course.name} "
                f"in **{slot.location}**"
            )

        embed.description = "\n".join(description_data)

        return embed


@dataclass
class ScheduleSlot:
    """A slot in the schedule"""

    course: UforaCourse
    start_time: datetime
    end_time: datetime
    location: str
    _hash: int = field(init=False)

    def __post_init__(self):
        """Fix some properties to display more nicely"""
        # Re-format the location data
        match = re.search(r"(.*)\. (?:Gebouw )?(.*)\. (?:Campus )?(.*)\. ", self.location)
        if match is not None:
            room, building, campus = match.groups()
            room = room.replace("PC / laptoplokaal ", "PC-lokaal")
            self.location = f"{campus} {building} {room}"

        # The same course can only start once at the same moment,
        # so this is guaranteed to be unique
        self._hash = hash(f"{self.course.course_id} {str(self.start_time)}")

    @property
    def alternative_overarching_role_id(self) -> Optional[int]:
        """Shortcut to getting the alternative overarching role id for this slot"""
        return self.course.alternative_overarching_role_id

    @property
    def overarching_role_id(self) -> Optional[int]:
        """Shortcut to getting the overarching role id for this slot"""
        return self.course.overarching_role_id

    @property
    def role_id(self) -> Optional[int]:
        """Shortcut to getting the role id for this slot"""
        return self.course.role_id

    @overrides
    def __hash__(self) -> int:
        return self._hash

    @overrides
    def __eq__(self, other):
        if not isinstance(other, ScheduleSlot):
            return False

        return self._hash == other._hash

    def could_merge_with(self, other: ScheduleSlot) -> bool:
        """Check if two slots are actually one with a 15-min break in-between

        If they are, merge the two into one (this edits the first slot in-place!)
        """
        if self.course.course_id != other.course.course_id:
            return False

        if self.location != other.location:
            return False

        if self.start_time == other.end_time:
            self.start_time = other.start_time
            self._hash = hash(f"{self.course.course_id} {str(self.start_time)}")
            return True
        elif self.end_time == other.start_time:
            self.end_time = other.end_time
            return True

        return False


def get_schedule_for_day(client: Didier, day_dt: date) -> Optional[Schedule]:
    """Get a schedule for an entire day"""
    main_schedule: Optional[Schedule] = None

    for schedule in client.schedules.values():
        personalized_schedule = schedule.on_day(day_dt)

        if not personalized_schedule:
            continue

        # Add the personalized one to the current main schedule
        if main_schedule is None:
            main_schedule = personalized_schedule
        else:
            main_schedule = main_schedule + personalized_schedule

    return main_schedule


def parse_course_code(summary: str) -> str:
    """Parse a course's code out of the summary"""
    code = re.search(r"^([^ ]+)\. ", summary)

    if code is None:
        return summary

    code_group = code.groups()[0]

    # Strip off last character as it's not relevant
    if code_group[-1].isalpha():
        return code_group[:-1]

    return code_group


def parse_time_string(string: str) -> datetime:
    """Parse an ISO string to a timezone-aware datetime instance"""
    return datetime.fromisoformat(string).astimezone(LOCAL_TIMEZONE)


async def parse_schedule_from_content(content: str, *, database_session: AsyncSession) -> Schedule:
    """Parse a schedule file, taking the file content as an argument

    This can be used to avoid unnecessarily opening the file again if you already have its contents
    """
    calendar = Calendar(content)
    events = list(calendar.events)
    course_codes: dict[str, UforaCourse] = {}
    slots: list[ScheduleSlot] = []

    for event in events:
        code = parse_course_code(event.name)

        if code not in course_codes:
            course = await get_course_by_code(database_session, code)
            if course is None:
                continue

            course_codes[code] = course

        # Overwrite the name to be the sanitized value
        event.name = code

        slot = ScheduleSlot(
            course=course_codes[code],
            start_time=parse_time_string(str(event.begin)),
            end_time=parse_time_string(str(event.end)),
            location=event.location,
        )

        # Slot extends another one, don't add it
        if any(s.could_merge_with(slot) for s in slots):
            continue

        slots.append(slot)

    # Cast to set at the END because the __hash__ can change while merging with others
    return Schedule(slots=set(slots))


async def parse_schedule(name: ScheduleType, *, database_session: AsyncSession) -> Optional[Schedule]:
    """Read and then parse a schedule file"""
    schedule_path = pathlib.Path(f"files/schedules/{name}.ics")
    if not schedule_path.exists():
        return None

    with open(schedule_path, "r", encoding="utf-8") as fp:
        return await parse_schedule_from_content(fp.read(), database_session=database_session)
