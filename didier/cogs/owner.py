from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from database.crud import custom_commands
from database.exceptions.constraints import DuplicateInsertException
from database.exceptions.not_found import NoResultFoundException
from didier import Didier
from didier.data.flags.owner import EditCustomFlags
from didier.views.modals import AddDadJoke, CreateCustomCommand, EditCustomCommand


class Owner(commands.Cog):
    """Cog for owner-only commands"""

    client: Didier

    # Slash groups
    add_slash = app_commands.Group(name="add", description="Add something new to the database")
    edit_slash = app_commands.Group(name="edit", description="Edit an existing database entry")

    def __init__(self, client: Didier):
        self.client = client

    async def cog_check(self, ctx: commands.Context) -> bool:
        """Global check for every command in this cog

        This means that we don't have to add is_owner() to every single command separately
        """
        return await self.client.is_owner(ctx.author)

    @commands.command(name="Error")
    async def _error(self, ctx: commands.Context):
        """Raise an exception for debugging purposes"""
        raise Exception("Debug")

    @commands.command(name="Sync")
    async def sync(self, ctx: commands.Context, guild: Optional[discord.Guild] = None):
        """Sync all application-commands in Discord"""
        if guild is not None:
            self.client.tree.copy_global_to(guild=guild)
            await self.client.tree.sync(guild=guild)
        else:
            await self.client.tree.sync()

        await ctx.message.add_reaction("🔄")

    @commands.group(name="Add", aliases=["Create"], case_insensitive=True, invoke_without_command=False)
    async def add_msg(self, ctx: commands.Context):
        """Command group for [add X] message commands"""

    @add_msg.command(name="Custom")
    async def add_custom(self, ctx: commands.Context, name: str, *, response: str):
        """Add a new custom command"""
        async with self.client.db_session as session:
            try:
                await custom_commands.create_command(session, name, response)
                await self.client.confirm_message(ctx.message)
            except DuplicateInsertException:
                await ctx.reply("Er bestaat al een commando met deze naam.")
                await self.client.reject_message(ctx.message)

    @add_msg.command(name="Alias")
    async def add_alias(self, ctx: commands.Context, command: str, alias: str):
        """Add a new alias for a custom command"""
        async with self.client.db_session as session:
            try:
                await custom_commands.create_alias(session, command, alias)
                await self.client.confirm_message(ctx.message)
            except NoResultFoundException:
                await ctx.reply(f'Geen commando gevonden voor "{command}".')
                await self.client.reject_message(ctx.message)
            except DuplicateInsertException:
                await ctx.reply("Er bestaat al een commando met deze naam.")
                await self.client.reject_message(ctx.message)

    @add_slash.command(name="custom", description="Add a custom command")
    async def add_custom_slash(self, interaction: discord.Interaction):
        """Slash command to add a custom command"""
        if not await self.client.is_owner(interaction.user):
            return interaction.response.send_message(
                "Je hebt geen toestemming om dit commando uit te voeren.", ephemeral=True
            )

        modal = CreateCustomCommand(self.client)
        await interaction.response.send_modal(modal)

    @add_slash.command(name="dadjoke", description="Add a dad joke")
    async def add_dad_joke_slash(self, interaction: discord.Interaction):
        """Slash command to add a dad joke"""
        if not await self.client.is_owner(interaction.user):
            return interaction.response.send_message(
                "Je hebt geen toestemming om dit commando uit te voeren.", ephemeral=True
            )

        modal = AddDadJoke(self.client)
        await interaction.response.send_modal(modal)

    @commands.group(name="Edit", case_insensitive=True, invoke_without_command=False)
    async def edit_msg(self, ctx: commands.Context):
        """Command group for [edit X] commands"""

    @edit_msg.command(name="Custom")
    async def edit_custom_msg(self, ctx: commands.Context, command: str, *, flags: EditCustomFlags):
        """Edit an existing custom command"""
        async with self.client.db_session as session:
            try:
                await custom_commands.edit_command(session, command, flags.name, flags.response)
                return await self.client.confirm_message(ctx.message)
            except NoResultFoundException:
                await ctx.reply(f"Geen commando gevonden voor ``{command}``.")
                return await self.client.reject_message(ctx.message)

    @edit_slash.command(name="custom", description="Edit a custom command")
    @app_commands.describe(command="The name of the command to edit")
    async def edit_custom_slash(self, interaction: discord.Interaction, command: str):
        """Slash command to edit a custom command"""
        if not await self.client.is_owner(interaction.user):
            return interaction.response.send_message(
                "Je hebt geen toestemming om dit commando uit te voeren.", ephemeral=True
            )

        async with self.client.db_session as session:
            _command = await custom_commands.get_command(session, command)
            if _command is None:
                return await interaction.response.send_message(
                    f"Geen commando gevonden voor ``{command}``.", ephemeral=True
                )

            modal = EditCustomCommand(self.client, _command.name, _command.response)
            await interaction.response.send_modal(modal)


async def setup(client: Didier):
    """Load the cog"""
    await client.add_cog(Owner(client))
