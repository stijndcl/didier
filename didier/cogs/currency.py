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
    """Everything Dinks-related."""

    client: Didier

    def __init__(self, client: Didier):
        super().__init__()
        self.client = client

    @commands.command(name="award")  # type: ignore[arg-type]
    @commands.check(is_owner)
    async def award(
        self,
        ctx: commands.Context,
        user: discord.User,
        amount: typing.Annotated[int, abbreviated_number],
    ):
        """Award a user `amount` Didier Dinks."""
        async with self.client.postgres_session as session:
            await crud.add_dinks(session, user.id, amount)
            plural = pluralize("Didier Dink", amount)
            await ctx.reply(
                f"**{ctx.author.display_name}** has awarded **{user.display_name}** **{amount}** {plural}.",
                mention_author=False,
            )

    @commands.group(name="bank", aliases=["b"], case_insensitive=True, invoke_without_command=True)
    async def bank(self, ctx: commands.Context):
        """Show your Didier Bank information."""
        async with self.client.postgres_session as session:
            bank = await crud.get_bank(session, ctx.author.id)

        embed = discord.Embed(title=f"{ctx.author.display_name}'s Bank", colour=discord.Colour.blue())

        if ctx.author.avatar is not None:
            embed.set_thumbnail(url=ctx.author.avatar.url)

        embed.add_field(name="Interest level", value=bank.interest_level)
        embed.add_field(name="Capacity level", value=bank.capacity_level)
        embed.add_field(name="Currently invested", value=bank.invested, inline=False)

        await ctx.reply(embed=embed, mention_author=False)

    @commands.hybrid_command(name="dinks")  # type: ignore[arg-type]
    async def dinks(self, ctx: commands.Context):
        """Check your Didier Dinks."""
        async with self.client.postgres_session as session:
            bank = await crud.get_bank(session, ctx.author.id)
            plural = pluralize("Didier Dink", bank.dinks)
            await ctx.reply(f"**{ctx.author.display_name}** has **{bank.dinks}** {plural}.", mention_author=False)

    @commands.command(name="invest", aliases=["deposit", "dep"])  # type: ignore[arg-type]
    async def invest(self, ctx: commands.Context, amount: typing.Annotated[typing.Union[str, int], abbreviated_number]):
        """Invest `amount` Didier Dinks into your bank.

        The `amount`-argument can take both raw numbers, and abbreviations of big numbers. Additionally, passing
        `all` as the value will invest all of your Didier Dinks.

        Example usage:
        ```
        didier invest all
        didier invest 500
        didier invest 25k
        didier invest 5.3b
        ```
        """
        async with self.client.postgres_session as session:
            invested = await crud.invest(session, ctx.author.id, amount)
            plural = pluralize("Didier Dink", invested)

            if invested == 0:
                await ctx.reply("You don't have any Didier Dinks to invest.", mention_author=False)
            else:
                await ctx.reply(
                    f"**{ctx.author.display_name}** has invested **{invested}** {plural}.", mention_author=False
                )

    @commands.hybrid_command(name="nightly")  # type: ignore[arg-type]
    async def nightly(self, ctx: commands.Context):
        """Claim nightly Didier Dinks."""
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
