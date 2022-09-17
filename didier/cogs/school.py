from datetime import date
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
from didier.data.embeds.schedules import Schedule, get_schedule_for_user
from didier.exceptions import HTTPException, NotInMainGuildException
from didier.utils.discord.converters.time import DateTransformer
from didier.utils.discord.flags.school import StudyGuideFlags
from didier.utils.discord.users import to_main_guild_member
from didier.utils.types.datetime import skip_weekends


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
        name="les", description="Show your personalized schedule for a given day.", aliases=["Sched", "Schedule"]
    )
    @app_commands.rename(day_dt="date")
    async def les(self, ctx: commands.Context, day_dt: Optional[app_commands.Transform[date, DateTransformer]] = None):
        """Show your personalized schedule for a given day."""
        if day_dt is None:
            day_dt = date.today()

        day_dt = skip_weekends(day_dt)

        async with ctx.typing():
            try:
                member_instance = to_main_guild_member(self.client, ctx.author)

                # Always make sure there is at least one schedule in case it returns None
                # this allows proper error messages
                schedule = get_schedule_for_user(self.client, member_instance, day_dt) or Schedule()

                return await ctx.reply(embed=schedule.to_embed(day=day_dt), mention_author=False)

            except NotInMainGuildException:
                return await ctx.reply(f"You are not a member of {self.client.main_guild.name}.", mention_author=False)

    @commands.hybrid_command(
        name="menu",
        description="Show the menu in the Ghent University restaurants.",
        aliases=["Eten", "Food"],
    )
    @app_commands.rename(day_dt="date")
    async def menu(self, ctx: commands.Context, day_dt: Optional[app_commands.Transform[date, DateTransformer]] = None):
        """Show the menu in the Ghent University restaurants.

        Menus are Dutch, as a lot of dishes have very weird translations
        """
        if day_dt is None:
            day_dt = date.today()

        async with ctx.typing():
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
