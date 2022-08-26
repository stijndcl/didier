from typing import Literal, Optional

import discord
from discord import app_commands
from discord.ext import commands

import settings
from database.crud import custom_commands, links, memes, ufora_courses
from database.exceptions.constraints import DuplicateInsertException
from database.exceptions.not_found import NoResultFoundException
from didier import Didier
from didier.utils.discord.flags.owner import EditCustomFlags, SyncOptionFlags
from didier.views.modals import (
    AddDadJoke,
    AddDeadline,
    AddLink,
    CreateCustomCommand,
    EditCustomCommand,
)


class Owner(commands.Cog):
    """Cog for owner-only commands"""

    client: Didier

    # Slash groups
    add_slash = app_commands.Group(
        name="add",
        description="Add something new to the database",
        guild_ids=settings.DISCORD_OWNER_GUILDS,
        guild_only=True,
    )
    edit_slash = app_commands.Group(
        name="edit",
        description="Edit an existing database entry",
        guild_ids=settings.DISCORD_OWNER_GUILDS,
        guild_only=True,
    )

    def __init__(self, client: Didier):
        self.client = client

    async def cog_check(self, ctx: commands.Context) -> bool:
        """Global check for every command in this cog

        This means that we don't have to add is_owner() to every single command separately
        """
        return await self.client.is_owner(ctx.author)

    @commands.command(name="Error", aliases=["Raise"])
    async def _error(self, ctx: commands.Context, *, message: str = "Debug"):
        """Raise an exception for debugging purposes"""
        raise Exception(message)

    @commands.command(name="Sync")
    async def sync(
        self,
        ctx: commands.Context,
        guild: Optional[discord.Guild] = None,
        symbol: Optional[Literal["."]] = None,
        *,
        flags: SyncOptionFlags,
    ):
        """Sync all application-commands in Discord"""
        # Allow using "." to specify the current guild
        # When passing flags, and no guild was specified, default to the current guild as well
        # because these don't work on global syncs
        if guild is None and (symbol == "." or flags.clear or flags.copy_globals):
            guild = ctx.guild

        if guild is not None:
            if flags.clear:
                self.client.tree.clear_commands(guild=guild)

            if flags.copy_globals:
                self.client.tree.copy_global_to(guild=guild)

            await self.client.tree.sync(guild=guild)
        else:
            await self.client.tree.sync()

        await ctx.message.add_reaction("🔄")

    @commands.group(name="Add", aliases=["Create"], case_insensitive=True, invoke_without_command=False)
    async def add_msg(self, ctx: commands.Context):
        """Command group for [add X] message commands"""

    @add_msg.command(name="Alias")
    async def add_alias_msg(self, ctx: commands.Context, command: str, alias: str):
        """Add a new alias for a custom command"""
        async with self.client.postgres_session as session:
            try:
                await custom_commands.create_alias(session, command, alias)
                await self.client.confirm_message(ctx.message)
            except NoResultFoundException:
                await ctx.reply(f"No command found matching `{command}`.")
                await self.client.reject_message(ctx.message)
            except DuplicateInsertException:
                await ctx.reply("There is already a command with this name.")
                await self.client.reject_message(ctx.message)

    @add_msg.command(name="Custom")
    async def add_custom_msg(self, ctx: commands.Context, name: str, *, response: str):
        """Add a new custom command"""
        async with self.client.postgres_session as session:
            try:
                await custom_commands.create_command(session, name, response)
                await self.client.confirm_message(ctx.message)
            except DuplicateInsertException:
                await ctx.reply("There is already a command with this name.")
                await self.client.reject_message(ctx.message)

    @add_msg.command(name="Link")
    async def add_link_msg(self, ctx: commands.Context, name: str, url: str):
        """Add a new link"""
        async with self.client.postgres_session as session:
            await links.add_link(session, name, url)
            await self.client.database_caches.links.invalidate(session)

        await self.client.confirm_message(ctx.message)

    @add_slash.command(name="custom", description="Add a custom command")
    async def add_custom_slash(self, interaction: discord.Interaction):
        """Slash command to add a custom command"""
        if not await self.client.is_owner(interaction.user):
            return interaction.response.send_message("You don't have permission to run this command.", ephemeral=True)

        modal = CreateCustomCommand(self.client)
        await interaction.response.send_modal(modal)

    @add_slash.command(name="dadjoke", description="Add a dad joke")
    async def add_dad_joke_slash(self, interaction: discord.Interaction):
        """Slash command to add a dad joke"""
        if not await self.client.is_owner(interaction.user):
            return interaction.response.send_message("You don't have permission to run this command.", ephemeral=True)

        modal = AddDadJoke(self.client)
        await interaction.response.send_modal(modal)

    @add_slash.command(name="deadline", description="Add a deadline")
    @app_commands.describe(course="The name of the course to add a deadline for (aliases work too)")
    async def add_deadline_slash(self, interaction: discord.Interaction, course: str):
        """Slash command to add a deadline"""
        async with self.client.postgres_session as session:
            course_instance = await ufora_courses.get_course_by_name(session, course)

        if course_instance is None:
            return await interaction.response.send_message(f"No course found matching `{course}`.", ephemeral=True)

        modal = AddDeadline(self.client, course_instance)
        await interaction.response.send_modal(modal)

    @add_deadline_slash.autocomplete("course")
    async def _add_deadline_course_autocomplete(
        self, _: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        """Autocompletion for the 'course'-parameter"""
        return self.client.database_caches.ufora_courses.get_autocomplete_suggestions(current)

    @add_slash.command(name="link", description="Add a new link")
    async def add_link_slash(self, interaction: discord.Interaction):
        """Slash command to add new links"""
        if not await self.client.is_owner(interaction.user):
            return interaction.response.send_message("You don't have permission to run this command.", ephemeral=True)

        modal = AddLink(self.client)
        await interaction.response.send_modal(modal)

    @add_slash.command(name="meme", description="Add a new meme")
    async def add_meme_slash(self, interaction: discord.Interaction, name: str, imgflip_id: int, field_count: int):
        """Slash command to add new memes"""
        await interaction.response.defer(ephemeral=True)

        async with self.client.postgres_session as session:
            meme = await memes.add_meme(session, name, imgflip_id, field_count)
            if meme is None:
                return await interaction.followup.send("A meme with this name (or id) already exists.")

            await interaction.followup.send(f"Added meme `{meme.meme_id}`.")
            await self.client.database_caches.memes.invalidate(session)

    @commands.group(name="Edit", case_insensitive=True, invoke_without_command=False)
    async def edit_msg(self, ctx: commands.Context):
        """Command group for [edit X] commands"""

    @edit_msg.command(name="Custom")
    async def edit_custom_msg(self, ctx: commands.Context, command: str, *, flags: EditCustomFlags):
        """Edit an existing custom command"""
        async with self.client.postgres_session as session:
            try:
                await custom_commands.edit_command(session, command, flags.name, flags.response)
                return await self.client.confirm_message(ctx.message)
            except NoResultFoundException:
                await ctx.reply(f"No command found matching `{command}`.")
                return await self.client.reject_message(ctx.message)

    @edit_slash.command(name="custom", description="Edit a custom command")
    @app_commands.describe(command="The name of the command to edit")
    async def edit_custom_slash(self, interaction: discord.Interaction, command: str):
        """Slash command to edit a custom command"""
        if not await self.client.is_owner(interaction.user):
            return interaction.response.send_message("You don't have permission to run this command.", ephemeral=True)

        async with self.client.postgres_session as session:
            _command = await custom_commands.get_command(session, command)
            if _command is None:
                return await interaction.response.send_message(
                    f"No command found matching `{command}`.", ephemeral=True
                )

            modal = EditCustomCommand(self.client, _command.name, _command.response)
            await interaction.response.send_modal(modal)


async def setup(client: Didier):
    """Load the cog"""
    await client.add_cog(Owner(client))
