import typing

import discord
from discord.ext import commands

from database.crud import currency as crud
from database.exceptions.currency import DoubleNightly
from didier import Didier
from didier.utils.discord.checks import is_owner
from didier.utils.discord.converters import abbreviated_number
from didier.utils.types.string import pluralize


class Currency(commands.Cog):
    """Everything Dinks-related"""

    client: Didier

    def __init__(self, client: Didier):
        super().__init__()
        self.client = client

    @commands.command(name="Award")
    @commands.check(is_owner)
    async def award(self, ctx: commands.Context, user: discord.User, amount: abbreviated_number):  # type: ignore
        """Award a user a given amount of Didier Dinks"""
        amount = typing.cast(int, amount)

        async with self.client.db_session as session:
            await crud.add_dinks(session, user.id, amount)
            plural = pluralize("Didier Dink", amount)
            await ctx.reply(
                f"**{ctx.author.display_name}** heeft **{user.display_name}** **{amount}** {plural} geschonken.",
                mention_author=False,
            )

    @commands.hybrid_group(name="bank", case_insensitive=True, invoke_without_command=True)
    async def bank(self, ctx: commands.Context):
        """Show your Didier Bank information"""
        async with self.client.db_session as session:
            await crud.get_bank(session, ctx.author.id)

    @commands.hybrid_command(name="dinks")
    async def dinks(self, ctx: commands.Context):
        """Check your Didier Dinks"""
        async with self.client.db_session as session:
            bank = await crud.get_bank(session, ctx.author.id)
            plural = pluralize("Didier Dink", bank.dinks)
            await ctx.reply(f"**{ctx.author.display_name}** heeft **{bank.dinks}** {plural}.", mention_author=False)

    @commands.hybrid_command(name="nightly")
    async def nightly(self, ctx: commands.Context):
        """Claim nightly Dinks"""
        async with self.client.db_session as session:
            try:
                await crud.claim_nightly(session, ctx.author.id)
                await ctx.reply(f"Je hebt je dagelijkse **{crud.NIGHTLY_AMOUNT}** Didier Dinks geclaimd.")
            except DoubleNightly:
                await ctx.reply("Je hebt je nightly al geclaimd vandaag.", mention_author=False, ephemeral=True)


async def setup(client: Didier):
    """Load the cog"""
    await client.add_cog(Currency(client))
