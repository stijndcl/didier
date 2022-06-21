from typing import Optional

import discord
from discord.ext import commands

from database.crud import custom_commands
from database.exceptions.constraints import DuplicateInsertException
from database.exceptions.not_found import NoResultFoundException
from didier import Didier


class Owner(commands.Cog):
    """Cog for owner-only commands"""

    client: Didier

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
        await self.client.tree.sync(guild=guild)
        await ctx.message.add_reaction("🔄")

    @commands.group(name="Add", case_insensitive=True, invoke_without_command=False)
    async def add(self, ctx: commands.Context):
        """Command group for [add X] commands"""

    @add.command(name="Custom")
    async def add_custom(self, ctx: commands.Context, name: str, *, response: str):
        """Add a new custom command"""
        async with self.client.db_session as session:
            try:
                await custom_commands.create_command(session, name, response)
                await self.client.confirm_message(ctx.message)
            except DuplicateInsertException:
                await ctx.reply("Er bestaat al een commando met deze naam.")
                await self.client.reject_message(ctx.message)

    @add.command(name="Alias")
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

    @commands.group(name="Edit")
    async def edit(self, ctx: commands.Context):
        """Command group for [edit X] commands"""


async def setup(client: Didier):
    """Load the cog"""
    await client.add_cog(Owner(client))
