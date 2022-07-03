import typing

import discord
from discord.ext import commands

from database.crud import currency as crud
from database.exceptions.currency import DoubleNightly, NotEnoughDinks
from didier import Didier
from didier.utils.discord.checks import is_owner
from didier.utils.discord.converters import abbreviated_number
from database.utils.math.currency import capacity_upgrade_price, interest_upgrade_price, rob_upgrade_price
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

    @commands.group(name="bank", aliases=["B"], case_insensitive=True, invoke_without_command=True)
    async def bank(self, ctx: commands.Context):
        """Show your Didier Bank information"""
        async with self.client.db_session as session:
            bank = await crud.get_bank(session, ctx.author.id)

        embed = discord.Embed(colour=discord.Colour.blue())
        embed.set_author(name=f"Bank van {ctx.author.display_name}")
        embed.set_thumbnail(url=ctx.author.avatar.url)

        embed.add_field(name="Interest level", value=bank.interest_level)
        embed.add_field(name="Capaciteit level", value=bank.capacity_level)
        embed.add_field(name="Momenteel geïnvesteerd", value=bank.invested, inline=False)

        await ctx.reply(embed=embed, mention_author=False)

    @bank.group(name="Upgrade", aliases=["U", "Upgrades"], case_insensitive=True, invoke_without_command=True)
    async def bank_upgrades(self, ctx: commands.Context):
        """List the upgrades you can buy & their prices"""
        async with self.client.db_session as session:
            bank = await crud.get_bank(session, ctx.author.id)

        embed = discord.Embed(colour=discord.Colour.blue())
        embed.set_author(name="Bank upgrades")

        embed.add_field(
            name=f"Interest ({bank.interest_level})", value=str(interest_upgrade_price(bank.interest_level))
        )
        embed.add_field(
            name=f"Capaciteit ({bank.capacity_level})", value=str(capacity_upgrade_price(bank.capacity_level))
        )
        embed.add_field(name=f"Rob ({bank.rob_level})", value=str(rob_upgrade_price(bank.rob_level)))

        embed.set_footer(text="Didier Bank Upgrade [Categorie]")

        await ctx.reply(embed=embed, mention_author=False)

    @bank_upgrades.command(name="Capacity", aliases=["C"])
    async def bank_upgrade_capacity(self, ctx: commands.Context):
        """Upgrade the capacity level of your bank"""
        async with self.client.db_session as session:
            try:
                await crud.upgrade_capacity(session, ctx.author.id)
                await ctx.message.add_reaction("⏫")
            except NotEnoughDinks:
                await ctx.reply("Je hebt niet genoeg Didier Dinks om dit te doen.", mention_author=False)
                await self.client.reject_message(ctx.message)

    @bank_upgrades.command(name="Interest", aliases=["I"])
    async def bank_upgrade_interest(self, ctx: commands.Context):
        """Upgrade the interest level of your bank"""
        async with self.client.db_session as session:
            try:
                await crud.upgrade_interest(session, ctx.author.id)
                await ctx.message.add_reaction("⏫")
            except NotEnoughDinks:
                await ctx.reply("Je hebt niet genoeg Didier Dinks om dit te doen.", mention_author=False)
                await self.client.reject_message(ctx.message)

    @bank_upgrades.command(name="Rob", aliases=["R"])
    async def bank_upgrade_rob(self, ctx: commands.Context):
        """Upgrade the rob level of your bank"""
        async with self.client.db_session as session:
            try:
                await crud.upgrade_rob(session, ctx.author.id)
                await ctx.message.add_reaction("⏫")
            except NotEnoughDinks:
                await ctx.reply("Je hebt niet genoeg Didier Dinks om dit te doen.", mention_author=False)
                await self.client.reject_message(ctx.message)

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
