from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from database.crud import ufora_courses
from didier import Didier
from didier.utils.discord.flags.school import StudyGuideFlags


class School(commands.Cog):
    """School-related commands"""

    client: Didier

    # Context-menu references
    _pin_ctx_menu: app_commands.ContextMenu

    def __init__(self, client: Didier):
        self.client = client

        self._pin_ctx_menu = app_commands.ContextMenu(name="Pin", callback=self.pin_ctx)
        self.client.tree.add_command(self._pin_ctx_menu)

    async def cog_unload(self) -> None:
        """Remove the commands when the cog is unloaded"""
        self.client.tree.remove_command(self._pin_ctx_menu.name, type=self._pin_ctx_menu.type)

    @commands.command(name="Pin", usage="[Message]")
    async def pin(self, ctx: commands.Context, message: Optional[discord.Message] = None):
        """Pin a message in the current channel"""
        # If no message was passed, allow replying to the message that should be pinned
        if message is None and ctx.message.reference is not None:
            message = await self.client.resolve_message(ctx.message.reference)

        # Didn't fix it, sad
        if message is None:
            return await ctx.reply("Found no message to pin.", delete_after=10)

        if message.pinned:
            return await ctx.reply("This message is already pinned.", delete_after=10)

        if message.is_system():
            return await ctx.reply("Dus jij wil system messages pinnen?\nMag niet.")

        await message.pin(reason=f"Didier Pin by {ctx.author.display_name}")
        await message.add_reaction("📌")

    async def pin_ctx(self, interaction: discord.Interaction, message: discord.Message):
        """Pin a message in the current channel"""
        # Is already pinned
        if message.pinned:
            return await interaction.response.send_message("This message is already pinned.", ephemeral=True)

        if message.is_system():
            return await interaction.response.send_message(
                "Dus jij wil system messages pinnen?\nMag niet.", ephemeral=True
            )

        await message.pin(reason=f"Didier Pin by {interaction.user.display_name}")
        await message.add_reaction("📌")
        return await interaction.response.send_message("📌", ephemeral=True)

    @commands.hybrid_command(
        name="fiche", description="Sends the link to the study guide for [Course]", aliases=["guide", "studiefiche"]
    )
    @app_commands.describe(course="vak")
    async def study_guide(self, ctx: commands.Context, course: str, *, flags: StudyGuideFlags):
        """Create links to study guides"""
        async with self.client.postgres_session as session:
            ufora_course = await ufora_courses.get_course_by_name(session, course)

        if ufora_course is None:
            return await ctx.reply(f"Found no course matching ``{course}``", ephemeral=True)

        return await ctx.reply(
            f"https://studiekiezer.ugent.be/studiefiche/nl/{ufora_course.code}/{flags.year}",
            mention_author=False,
        )

    @study_guide.autocomplete("course")
    async def study_guide_autocomplete(self, _: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        """Autocompletion for the 'course'-parameter"""
        return [
            app_commands.Choice(name=course, value=course)
            for course in self.client.database_caches.ufora_courses.get_autocomplete_suggestions(current)
        ]


async def setup(client: Didier):
    """Load the cog"""
    await client.add_cog(School(client))
