import typing

import discord
from discord.ext import commands

from database.crud import currency as crud
from database.exceptions.currency import DoubleNightly, NotEnoughDinks
from database.utils.math.currency import (
    capacity_upgrade_price,
    interest_upgrade_price,
    rob_upgrade_price,
)
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

    @commands.command(name="award")
    @commands.check(is_owner)
    async def award(
        self,
        ctx: commands.Context,
        user: discord.User,
        amount: typing.Annotated[int, abbreviated_number],
    ):
        """Award a user a given amount of Didier Dinks"""
        async with self.client.postgres_session as session:
            await crud.add_dinks(session, user.id, amount)
            plural = pluralize("Didier Dink", amount)
            await ctx.reply(
                f"**{ctx.author.display_name}** has awarded **{user.display_name}** **{amount}** {plural}.",
                mention_author=False,
            )

    @commands.group(name="bank", aliases=["b"], case_insensitive=True, invoke_without_command=True)
    async def bank(self, ctx: commands.Context):
        """Show your Didier Bank information"""
        async with self.client.postgres_session as session:
            bank = await crud.get_bank(session, ctx.author.id)

        embed = discord.Embed(title=f"{ctx.author.display_name}'s Bank", colour=discord.Colour.blue())
        embed.set_thumbnail(url=ctx.author.avatar.url)

        embed.add_field(name="Interest level", value=bank.interest_level)
        embed.add_field(name="Capacity level", value=bank.capacity_level)
        embed.add_field(name="Currently invested", value=bank.invested, inline=False)

        await ctx.reply(embed=embed, mention_author=False)

    @bank.group(name="upgrade", aliases=["u", "upgrades"], case_insensitive=True, invoke_without_command=True)
    async def bank_upgrades(self, ctx: commands.Context):
        """List the upgrades you can buy & their prices"""
        async with self.client.postgres_session as session:
            bank = await crud.get_bank(session, ctx.author.id)

        embed = discord.Embed(title="Bank upgrades", colour=discord.Colour.blue())

        embed.add_field(
            name=f"Interest ({bank.interest_level})", value=str(interest_upgrade_price(bank.interest_level))
        )
        embed.add_field(
            name=f"Capacity ({bank.capacity_level})", value=str(capacity_upgrade_price(bank.capacity_level))
        )
        embed.add_field(name=f"Rob ({bank.rob_level})", value=str(rob_upgrade_price(bank.rob_level)))

        embed.set_footer(text="Didier Bank Upgrade [Category]")

        await ctx.reply(embed=embed, mention_author=False)

    @bank_upgrades.command(name="capacity", aliases=["c"])
    async def bank_upgrade_capacity(self, ctx: commands.Context):
        """Upgrade the capacity level of your bank"""
        async with self.client.postgres_session as session:
            try:
                await crud.upgrade_capacity(session, ctx.author.id)
                await ctx.message.add_reaction("⏫")
            except NotEnoughDinks:
                await ctx.reply("You don't have enough Didier Dinks to do this.", mention_author=False)
                await self.client.reject_message(ctx.message)

    @bank_upgrades.command(name="interest", aliases=["i"])
    async def bank_upgrade_interest(self, ctx: commands.Context):
        """Upgrade the interest level of your bank"""
        async with self.client.postgres_session as session:
            try:
                await crud.upgrade_interest(session, ctx.author.id)
                await ctx.message.add_reaction("⏫")
            except NotEnoughDinks:
                await ctx.reply("You don't have enough Didier Dinks to do this.", mention_author=False)
                await self.client.reject_message(ctx.message)

    @bank_upgrades.command(name="rob", aliases=["r"])
    async def bank_upgrade_rob(self, ctx: commands.Context):
        """Upgrade the rob level of your bank"""
        async with self.client.postgres_session as session:
            try:
                await crud.upgrade_rob(session, ctx.author.id)
                await ctx.message.add_reaction("⏫")
            except NotEnoughDinks:
                await ctx.reply("You don't have enough Didier Dinks to do this.", mention_author=False)
                await self.client.reject_message(ctx.message)

    @commands.hybrid_command(name="dinks")
    async def dinks(self, ctx: commands.Context):
        """Check your Didier Dinks"""
        async with self.client.postgres_session as session:
            bank = await crud.get_bank(session, ctx.author.id)
            plural = pluralize("Didier Dink", bank.dinks)
            await ctx.reply(f"**{ctx.author.display_name}** has **{bank.dinks}** {plural}.", mention_author=False)

    @commands.command(name="invest", aliases=["deposit", "dep"])
    async def invest(self, ctx: commands.Context, amount: typing.Annotated[typing.Union[str, int], abbreviated_number]):
        """Invest a given amount of Didier Dinks"""
        async with self.client.postgres_session as session:
            invested = await crud.invest(session, ctx.author.id, amount)
            plural = pluralize("Didier Dink", invested)

            if invested == 0:
                await ctx.reply("You don't have any Didier Dinks to invest.", mention_author=False)
            else:
                await ctx.reply(
                    f"**{ctx.author.display_name}** has invested **{invested}** {plural}.", mention_author=False
                )

    @commands.hybrid_command(name="nightly")
    async def nightly(self, ctx: commands.Context):
        """Claim nightly Didier Dinks"""
        async with self.client.postgres_session as session:
            try:
                await crud.claim_nightly(session, ctx.author.id)
                await ctx.reply(f"You've claimed your daily **{crud.NIGHTLY_AMOUNT}** Didier Dinks.")
            except DoubleNightly:
                await ctx.reply(
                    "You've already claimed your Didier Nightly today.", mention_author=False, ephemeral=True
                )


async def setup(client: Didier):
    """Load the cog"""
    await client.add_cog(Currency(client))
