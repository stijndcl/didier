from dataclasses import dataclass
from typing import Optional

import dacite
import json


@dataclass
class Course:
    abbreviations: list[str]
    code: str
    name: str
    year: int
    alt: Optional[str] = None


def load_courses() -> dict[str, Course]:
    """Create a list of all courses"""
    with open("files/courses.json", "r") as file:
        data = json.load(file)

    courses = {}

    for course_name in data:
        # Add name into the dict to allow flexibility
        course_data = data[course_name]
        course_data["name"] = course_name

        courses[course_name] = dacite.from_dict(data_class=Course, data=course_data)

    return courses


def find_course_from_name(name: str, courses: Optional[dict[str, Course]] = None, case_insensitive: bool = True) -> Optional[Course]:
    # Allow passing a course dict in to avoid having to create it all the time
    if courses is None:
        courses = load_courses()

    if case_insensitive:
        name = name.lower()

    def _perhaps_lower(inp: str) -> str:
        """Cast a string to lowercase if necessary"""
        if case_insensitive:
            return inp.lower()

        return inp

    # Iterate over all courses to look for a match
    for course_name, course in courses.items():
        # Check name first
        if _perhaps_lower(course_name) == name:
            return course

        # Then abbreviations
        for abbreviation in course.abbreviations:
            if _perhaps_lower(abbreviation) == name:
                return course

        # Finally alternative names
        if course.alt is not None and _perhaps_lower(course.alt) == name:
            return course

    return None
