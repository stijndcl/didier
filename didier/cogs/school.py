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
from didier.data.embeds.schedules import Schedule, get_schedule_for_day
from didier.exceptions import HTTPException, NotInMainGuildException
from didier.utils.discord.converters.time import DateTransformer
from didier.utils.discord.flags.school import StudyGuideFlags
from didier.utils.discord.users import has_course, to_main_guild_member
from didier.utils.types.datetime import skip_weekends, tz_aware_today


class School(commands.Cog):
    """School-related commands"""

    client: Didier

    def __init__(self, client: Didier):
        self.client = client

    @commands.hybrid_command(name="deadlines")
    async def deadlines(self, ctx: commands.Context):
        """Show upcoming deadlines."""
        async with ctx.typing():
            async with self.client.postgres_session as session:
                deadlines = await get_deadlines(session, after=tz_aware_today())

            member = to_main_guild_member(self.client, ctx.author)
            deadlines = list(filter(lambda d: has_course(member, d.course), deadlines))

            embed = Deadlines(deadlines).to_embed()
            await ctx.reply(embed=embed, mention_author=False, ephemeral=False)

    @commands.hybrid_command(name="les", aliases=["sched", "schedule"])
    @app_commands.rename(day_dt="date")
    async def les(
        self, ctx: commands.Context, *, day_dt: Optional[app_commands.Transform[date, DateTransformer]] = None
    ):
        """Show your personalized schedule for a given day.

        If no day is provided, this defaults to the schedule for the current day. When invoked during a weekend,
        it will skip forward to the next weekday instead.

        Schedules are personalized based on your roles in the server. If your schedule doesn't look right, make sure
        that you've got the correct roles selected. In case you do, ping D STIJN.
        """
        async with ctx.typing():
            if day_dt is None:
                day_dt = tz_aware_today()

            day_dt = skip_weekends(day_dt)

            try:
                member_instance = to_main_guild_member(self.client, ctx.author)
                roles = {role.id for role in member_instance.roles}

                # Always make sure there is at least one schedule in case it returns None
                # this allows proper error messages
                schedule = (get_schedule_for_day(self.client, day_dt) or Schedule()).personalize(roles)

                return await ctx.reply(embed=schedule.to_embed(day=day_dt), mention_author=False)

            except NotInMainGuildException:
                return await ctx.reply(f"You are not a member of {self.client.main_guild.name}.", mention_author=False)

    @commands.hybrid_command(
        name="menu",
        aliases=["eten", "food"],
    )
    @app_commands.rename(day_dt="date")
    async def menu(
        self, ctx: commands.Context, *, day_dt: Optional[app_commands.Transform[date, DateTransformer]] = None
    ):
        """Show the menu in the Ghent University restaurants on `date`.

        If no value for `date` is provided, this defaults to the schedule for the current day.
        Menus are shown in Dutch by default, as a lot of dishes have very weird translations.
        """
        if day_dt is None:
            day_dt = tz_aware_today()

        async with ctx.typing():
            try:
                menu = await fetch_menu(self.client.http_session, day_dt)
                embed = menu.to_embed(day_dt=day_dt)
            except HTTPException:
                embed = no_menu_found(day_dt)
            await ctx.reply(embed=embed, mention_author=False)

    @commands.hybrid_command(
        name="fiche", description="Sends the link to study guides", aliases=["guide", "studiefiche"]
    )
    @app_commands.describe(course="The name of the course to fetch the study guide for (aliases work too)")
    async def study_guide(self, ctx: commands.Context, course: str, *, flags: StudyGuideFlags):
        """Sends the link to the study guide for `course`.

        The value for `course` can contain spaces, but must be wrapped in "quotes".

        Aliases (nicknames) for courses are also accepted, given that they are known and in the database.

        Example usage:
        ```
        didier fiche ad2
        didier fiche "algoritmen en datastructuren 2"
        ```
        """
        async with self.client.postgres_session as session:
            ufora_course = await ufora_courses.get_course_by_name(session, course)

        if ufora_course is None:
            return await ctx.reply(f"Found no course matching `{course}`", ephemeral=True)

        return await ctx.reply(
            f"https://studiekiezer.ugent.be/studiefiche/nl/{ufora_course.code}/{flags.year}",
            mention_author=False,
        )

    @commands.hybrid_command(name="ufora")
    async def ufora(self, ctx: commands.Context, course: str):
        """Link the Ufora page for a course."""
        async with self.client.postgres_session as session:
            ufora_course = await ufora_courses.get_course_by_name(session, course)

        if ufora_course is None:
            return await ctx.reply(f"Found no course matching `{course}`", ephemeral=True)

        return await ctx.reply(
            f"https://ufora.ugent.be/d2l/le/content/{ufora_course.course_id}/home", mention_author=False
        )

    @study_guide.autocomplete("course")
    @ufora.autocomplete("course")
    async def _course_autocomplete(self, _: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        """Autocompletion for the 'course'-parameter"""
        return self.client.database_caches.ufora_courses.get_autocomplete_suggestions(current)


async def setup(client: Didier):
    """Load the cog"""
    await client.add_cog(School(client))
