from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from database.crud import custom_commands
from database.exceptions.constraints import DuplicateInsertException
from database.exceptions.not_found import NoResultFoundException
from didier import Didier
from didier.data.modals.custom_commands import CreateCustomCommand


class Owner(commands.Cog):
    """Cog for owner-only commands"""

    client: Didier

    # Slash groups
    add_slash = app_commands.Group(name="add", description="Add something new to the database")

    def __init__(self, client: Didier):
        self.client = client

    async def cog_check(self, ctx: commands.Context) -> bool:
        """Global check for every command in this cog, so we don't have to add
        is_owner() to every single command separately
        """
        return await self.client.is_owner(ctx.author)

    @commands.command(name="Sync")
    async def sync(self, ctx: commands.Context, guild: Optional[discord.Guild] = None):
        """Sync all application-commands in Discord"""
        if guild is not None:
            self.client.tree.copy_global_to(guild=guild)
            await self.client.tree.sync(guild=guild)
        else:
            self.client.tree.clear_commands(guild=None)
            await self.client.tree.sync()

        await ctx.message.add_reaction("🔄")

    @commands.group(name="Add", case_insensitive=True, invoke_without_command=False)
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
        if not self.client.is_owner(interaction.user):
            return interaction.response.send_message(
                "Je hebt geen toestemming om dit commando uit te voeren.", ephemeral=True
            )

        await interaction.response.defer(ephemeral=True)
        modal = CreateCustomCommand()
        await interaction.response.send_message(modal)

    @commands.group(name="Edit")
    async def edit(self, ctx: commands.Context):
        """Command group for [edit X] commands"""


async def setup(client: Didier):
    """Load the cog"""
    await client.add_cog(Owner(client))
