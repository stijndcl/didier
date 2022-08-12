import itertools
from datetime import datetime

import discord
from overrides import overrides

from database.schemas.relational import Deadline
from didier.data.embeds.base import EmbedBaseModel
from didier.utils.types.datetime import tz_aware_now
from didier.utils.types.string import get_edu_year_name

__all__ = ["Deadlines"]


class Deadlines(EmbedBaseModel):
    """Embed that shows all the deadlines of a semester"""

    deadlines: list[Deadline]

    def __init__(self, deadlines: list[Deadline]):
        self.deadlines = deadlines
        self.deadlines.sort(key=lambda deadline: deadline.deadline)

    @overrides
    def to_embed(self, **kwargs: dict) -> discord.Embed:
        embed = discord.Embed(colour=discord.Colour.dark_gold())
        embed.set_author(name="Upcoming Deadlines")
        now = tz_aware_now()

        has_active_deadlines = False
        deadlines_grouped: dict[int, list[str]] = {}

        for year, deadlines in itertools.groupby(self.deadlines, key=lambda _deadline: _deadline.course.year):
            if year not in deadlines_grouped:
                deadlines_grouped[year] = []

            for deadline in deadlines:
                passed = deadline.deadline <= now
                if not passed:
                    has_active_deadlines = True

                deadline_str = (
                    f"{deadline.course.name} - {deadline.name}: <t:{round(datetime.timestamp(deadline.deadline))}:R>"
                )

                # Strike through deadlines that aren't active anymore
                deadlines_grouped[year].append(deadline_str if not passed else f"~~{deadline_str}~~")

        # Send an Easter egg when there are no deadlines
        if not has_active_deadlines:
            embed.description = "There are currently no upcoming deadlines."
            embed.set_image(url="https://c.tenor.com/RUzJ3lDGQUsAAAAC/iron-man-you-can-rest-now.gif")
            return embed

        for i in range(1, 6):
            if i not in deadlines_grouped:
                continue

            name = get_edu_year_name(i - 1)
            description = "\n".join(deadlines_grouped[i])

            embed.add_field(name=name, value=description, inline=False)

        return embed
