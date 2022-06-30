import discord
from discord.ext import commands

from didier import Didier

from database.crud import currency as crud
from database.exceptions.currency import DoubleNightly
from didier.utils.discord.checks import is_owner
from didier.utils.types.string import pluralize


class Currency(commands.Cog):
    """Everything Dinks-related"""

    client: Didier

    def __init__(self, client: Didier):
        super().__init__()
        self.client = client

    @commands.command(name="Award")
    @commands.check(is_owner)
    async def award(self, ctx: commands.Context, user: discord.User, amount: int):
        async with self.client.db_session as session:
            await crud.add_dinks(session, user.id, amount)
            await self.client.confirm_message(ctx.message)

    @commands.hybrid_command(name="bank")
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
    await client.add_cog(Currency(client))
