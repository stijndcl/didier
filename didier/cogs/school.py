from datetime import datetime
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from database.crud import ufora_courses
from database.crud.deadlines import get_deadlines
from didier import Didier
from didier.data.apis.hydra import fetch_menu
from didier.data.embeds.deadlines import Deadlines
from didier.data.embeds.hydra import no_menu_found
from didier.exceptions import HTTPException
from didier.utils.discord.flags.school import StudyGuideFlags


class School(commands.Cog):
    """School-related commands"""

    client: Didier

    def __init__(self, client: Didier):
        self.client = client

    @commands.hybrid_command(name="deadlines", description="Show upcoming deadlines")
    async def deadlines(self, ctx: commands.Context):
        """Show upcoming deadlines"""
        async with self.client.postgres_session as session:
            deadlines = await get_deadlines(session)

        embed = Deadlines(deadlines).to_embed()
        await ctx.reply(embed=embed, mention_author=False, ephemeral=False)

    @commands.hybrid_command(
        name="menu",
        description="Show the menu in the Ghent University restaurants.",
        aliases=["Eten", "Food"],
    )
    async def menu(self, ctx: commands.Context, day: Optional[str] = None):
        """Show the menu in the Ghent University restaurants.

        Menus are Dutch, as a lot of dishes have very weird translations
        """
        # TODO time converter (transformer) for [DAY]
        # TODO autocompletion for [DAY]
        async with ctx.typing():
            day_dt = datetime(year=2022, month=8, day=29)

            try:
                menu = await fetch_menu(self.client.http_session, day_dt)
                embed = menu.to_embed(day_dt=day_dt)
            except HTTPException:
                embed = no_menu_found(day_dt)
            await ctx.reply(embed=embed, mention_author=False)

    @commands.hybrid_command(
        name="fiche", description="Sends the link to the study guide for [Course]", aliases=["guide", "studiefiche"]
    )
    @app_commands.describe(course="The name of the course to fetch the study guide for (aliases work too)")
    async def study_guide(self, ctx: commands.Context, course: str, *, flags: StudyGuideFlags):
        """Create links to study guides"""
        async with self.client.postgres_session as session:
            ufora_course = await ufora_courses.get_course_by_name(session, course)

        if ufora_course is None:
            return await ctx.reply(f"Found no course matching `{course}`", ephemeral=True)

        return await ctx.reply(
            f"https://studiekiezer.ugent.be/studiefiche/nl/{ufora_course.code}/{flags.year}",
            mention_author=False,
        )

    @study_guide.autocomplete("course")
    async def _study_guide_course_autocomplete(
        self, _: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        """Autocompletion for the 'course'-parameter"""
        return self.client.database_caches.ufora_courses.get_autocomplete_suggestions(current)


async def setup(client: Didier):
    """Load the cog"""
    await client.add_cog(School(client))
