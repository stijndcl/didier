import json
import time
from dataclasses import dataclass

from discord import Embed, Colour
from functions.stringFormatters import get_edu_year
from typing import Dict

"""
Sample json structure:
{
    "1": {
        "ad1": {
            "proj1": 123456789
        }
    }
}
"""


@dataclass
class Deadline:
    course: str
    name: str
    t: int
    passed: bool

    def __str__(self) -> str:
        v = f"{self.course} - {self.name}: <t:{self.t}:R>"

        if self.passed:
            v = f"~~v~~"

        return v


class Deadlines:
    data: Dict

    def __init__(self):
        with open("files/deadlines.json") as f:
            self.data = json.load(f)

    def to_embed(self) -> Embed:
        embed = Embed(colour=Colour.dark_gold())
        embed.set_author(name="Aanstaande Deadlines")

        now = time.time()

        if not self.data:
            embed.description = "Er staan geen deadlines gepland."
            return embed

        courses: Dict
        for year, courses in sorted(self.data.items(), key=lambda x: x[0]):
            content = []

            deadlines: Dict[str, int]
            for course, deadlines in courses.items():
                for deadline, t in deadlines.items():
                    content.append(Deadline(course, deadline, t, t < now))

            content.sort(key=lambda x: x.t)
            content = map(lambda x: str(x), content)

            embed.add_field(name=get_edu_year(int(year)), value="\n".join(content), inline=False)

        return embed
