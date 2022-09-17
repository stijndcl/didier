from __future__ import annotations

import pathlib
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from arrow import Arrow
from ics import Calendar
from overrides import overrides
from sqlalchemy.ext.asyncio import AsyncSession

from database.crud.ufora_courses import get_course_by_code
from database.schemas import UforaCourse
from didier.utils.types.datetime import LOCAL_TIMEZONE
from settings import ScheduleType

__all__ = ["Schedule", "parse_schedule_from_content", "parse_schedule"]


@dataclass
class Schedule:
    """An entire schedule"""

    slots: set[ScheduleSlot]


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
        room, building, campus = re.search(r"Leslokaal (.*)\. Gebouw (.*)\. Campus (.*)\. ", self.location).groups()
        self.location = f"{campus} {building} {room}"

        self._hash = hash(f"{self.course.course_id} {str(self.start_time)}")

    @overrides
    def __hash__(self) -> int:
        return self._hash

    @overrides
    def __eq__(self, other: ScheduleSlot):
        return self._hash == other._hash


def parse_course_code(summary: str) -> str:
    """Parse a course's code out of the summary"""
    code = re.search(r"^([^ ]+)\. ", summary).groups()[0]

    # Strip off last character as it's not relevant
    if code[-1].isalpha():
        return code[:-1]

    return code


def parse_time_string(string: str) -> datetime:
    """Parse an ISO string to a timezone-aware datetime instance"""
    return datetime.fromisoformat(string).astimezone(LOCAL_TIMEZONE)


async def parse_schedule_from_content(content: str, *, database_session: AsyncSession) -> Schedule:
    """Parse a schedule file, taking the file content as an argument

    This can be used to avoid unnecessarily opening the file again if you already have its contents
    """
    calendar = Calendar(content)
    day = Arrow(year=2022, month=9, day=26)
    events = list(calendar.timeline.on(day))
    course_codes: dict[str, UforaCourse] = {}
    slots: set[ScheduleSlot] = set()

    for event in events:
        code = parse_course_code(event.name)

        if code not in course_codes:
            course = await get_course_by_code(database_session, code)
            if course is None:
                # raise ValueError(f"Unable to find course with code {code} (event {event.name})")
                continue  # TODO uncomment the line above

            course_codes[code] = course

        # Overwrite the name to be the sanitized value
        event.name = code

        slot = ScheduleSlot(
            course=course_codes[code],
            start_time=parse_time_string(str(event.begin)),
            end_time=parse_time_string(str(event.end)),
            location=event.location,
        )

        slots.add(slot)

    return Schedule(slots=slots)


async def parse_schedule(name: ScheduleType, *, database_session: AsyncSession) -> Optional[Schedule]:
    """Read and then parse a schedule file"""
    schedule_path = pathlib.Path(f"files/schedules/{name}.ics")
    if not schedule_path.exists():
        return None

    with open(schedule_path, "r", encoding="utf-8") as fp:
        return await parse_schedule_from_content(fp.read(), database_session=database_session)
