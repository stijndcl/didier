# flake8: noqa: E800
import asyncio
import math
import random
import typing
from datetime import timedelta

import discord
from discord.ext import commands

import settings
from database.crud import currency as crud
from database.crud import users
from database.crud.jail import get_user_jail, imprison
from database.exceptions.currency import (
    DoubleNightly,
    NotEnoughDinks,
    SavingsCapExceeded,
)
from database.utils.math.currency import (
    capacity_upgrade_price,
    interest_rate,
    interest_upgrade_price,
    jail_chance,
    jail_time,
    rob_amount,
    rob_chance,
    rob_upgrade_price,
    savings_cap,
)
from didier import Didier
from didier.utils.discord import colours
from didier.utils.discord.checks import is_owner
from didier.utils.discord.converters import abbreviated_number
from didier.utils.types.datetime import tz_aware_now
from didier.utils.types.string import pluralize


class Currency(commands.Cog):
    """Everything Dinks-related."""

    client: Didier
    _rob_lock: asyncio.Lock

    def __init__(self, client: Didier):
        super().__init__()
        self.client = client
        self._rob_lock = asyncio.Lock()

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
            f"{ctx.author.display_name} has awarded **{user.display_name}** with **{amount}** {plural}.",
            mention_author=False,
        )

    @commands.group(name="bank", aliases=["b"], case_insensitive=True, invoke_without_command=True)
    async def bank(self, ctx: commands.Context):
        """Show your Didier Bank information."""
        async with self.client.postgres_session as session:
            user = await users.get_or_add_user(session, ctx.author.id)
            bank = user.bank
            savings = user.savings

        embed = discord.Embed(title="Bank of Didier", colour=discord.Colour.blue())
        embed.set_author(name=ctx.author.display_name)

        if ctx.author.avatar is not None:
            embed.set_thumbnail(url=ctx.author.avatar.url)

        embed.add_field(name="Interest rate", value=round(interest_rate(bank.interest_level), 2))
        embed.add_field(name="Maximum capacity", value=round(savings_cap(bank.capacity_level), 2))
        embed.add_field(name="Currently saved", value=savings.saved, inline=False)
        embed.add_field(name="Daily minimum", value=savings.daily_minimum, inline=False)

        await ctx.reply(embed=embed, mention_author=False)

    @bank.group(  # type: ignore[arg-type]
        name="upgrade", aliases=["u", "upgrades"], case_insensitive=True, invoke_without_command=True
    )
    async def bank_upgrades(self, ctx: commands.Context):
        """List the upgrades you can buy & their prices."""
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

    @bank_upgrades.command(name="capacity", aliases=["c"])  # type: ignore[arg-type]
    async def bank_upgrade_capacity(self, ctx: commands.Context):
        """Upgrade the capacity level of your bank."""
        async with self.client.postgres_session as session:
            try:
                await crud.upgrade_capacity(session, ctx.author.id)
                await ctx.message.add_reaction("⏫")
            except NotEnoughDinks:
                await ctx.reply("You don't have enough Didier Dinks to do this.", mention_author=False)
                await self.client.reject_message(ctx.message)

    @bank_upgrades.command(name="interest", aliases=["i"])  # type: ignore[arg-type]
    async def bank_upgrade_interest(self, ctx: commands.Context):
        """Upgrade the interest level of your bank."""
        async with self.client.postgres_session as session:
            try:
                await crud.upgrade_interest(session, ctx.author.id)
                await ctx.message.add_reaction("⏫")
            except NotEnoughDinks:
                await ctx.reply("You don't have enough Didier Dinks to do this.", mention_author=False)
                await self.client.reject_message(ctx.message)

    @bank_upgrades.command(name="rob", aliases=["r"])  # type: ignore[arg-type]
    async def bank_upgrade_rob(self, ctx: commands.Context):
        """Upgrade the rob level of your bank."""
        async with self.client.postgres_session as session:
            try:
                await crud.upgrade_rob(session, ctx.author.id)
                await ctx.message.add_reaction("⏫")
            except NotEnoughDinks:
                await ctx.reply("You don't have enough Didier Dinks to do this.", mention_author=False)
                await self.client.reject_message(ctx.message)

    @commands.hybrid_command(name="dinks")  # type: ignore[arg-type]
    async def dinks(self, ctx: commands.Context):
        """Check your Didier Dinks."""
        async with ctx.typing(), self.client.postgres_session as session:
            bank = await crud.get_bank(session, ctx.author.id)

        plural = pluralize("Didier Dink", bank.dinks)
        await ctx.reply(f"You have **{bank.dinks}** {plural}.", mention_author=False)

    @commands.command(name="save", aliases=["deposit", "dep", "s"])  # type: ignore[arg-type]
    async def save(self, ctx: commands.Context, amount: typing.Annotated[typing.Union[str, int], abbreviated_number]):
        """Add `amount` Didier Dinks into your bank's savings account.

        The `amount`-argument can take both raw numbers, and abbreviations of big numbers. Additionally, passing
        `all` or `*` as the value will invest all of your Didier Dinks.

        Example usage:
        ```
        didier save all
        didier save 500
        didier save 25k
        didier save 5.3b
        ```
        """
        if isinstance(amount, int) and amount <= 0:
            return await ctx.reply("Amount of Didier Dinks to invest must be a strictly positive integer.")

        async with self.client.postgres_session as session:
            try:
                saved = await crud.save(session, ctx.author.id, amount)
            except SavingsCapExceeded:
                return await ctx.reply(
                    "You have already exceeded the savings cap for your level. Upgrade your bank's capacity to save "
                    "more."
                )

        plural = pluralize("Didier Dink", saved)

        if saved == 0:
            await ctx.reply("You don't have any Didier Dinks to invest.", mention_author=False)
        else:
            await ctx.reply(f"You have saved **{saved}** {plural}.", mention_author=False)

    @commands.command(name="withdraw", aliases=["undeposit", "unsave", "w"])  # type: ignore[arg-type]
    async def withdraw(
        self, ctx: commands.Context, amount: typing.Annotated[typing.Union[str, int], abbreviated_number]
    ):
        """Withdraw some of your Didier Dinks from your bank's savings account."""
        if isinstance(amount, int) and amount <= 0:
            return await ctx.reply("Amount of Didier Dinks to invest must be a strictly positive integer.")

        async with self.client.postgres_session as session:
            withdrawn = await crud.withdraw(session, ctx.author.id, amount)

        plural = pluralize("Didier Dink", withdrawn)

        if withdrawn == 0:
            await ctx.reply("You don't have any Didier Dinks to withdraw.", mention_author=False)
        else:
            await ctx.reply(f"You have withdrawn **{withdrawn}** {plural}.", mention_author=False)

    @commands.hybrid_command(name="nightly")  # type: ignore[arg-type]
    async def nightly(self, ctx: commands.Context):
        """Claim nightly Didier Dinks."""
        async with ctx.typing(), self.client.postgres_session as session:
            try:
                await crud.claim_nightly(session, ctx.author.id)
                await ctx.reply(
                    f"You've claimed your daily **{crud.NIGHTLY_AMOUNT}** Didier Dinks.", mention_author=False
                )
            except DoubleNightly:
                await ctx.reply(
                    "You've already claimed your Didier Nightly today.", mention_author=False, ephemeral=True
                )

    @commands.hybrid_command(name="rob")  # type: ignore[arg-type]
    @commands.cooldown(rate=1, per=10 * 60.0, type=commands.BucketType.user)
    @commands.guild_only()
    async def rob(self, ctx: commands.Context, member: discord.Member):
        """Attempt to rob another user of their Dinks"""
        if member == ctx.author:
            return await ctx.reply("You can't rob yourself.", mention_author=False, ephemeral=True)

        if member == self.client.user:
            return await ctx.reply(settings.DISCORD_BOOS_REACT, mention_author=False)

        if member.bot:
            return await ctx.reply("You can't rob bots.", mention_author=False, ephemeral=True)

        # Use a Lock for robbing to avoid race conditions when robbing the same person twice
        # This would lead to undefined behaviour
        # Typing() must come first for slash commands
        async with ctx.typing(), self._rob_lock, self.client.postgres_session as session:
            robber = await crud.get_bank(session, ctx.author.id)
            robbed = await crud.get_bank(session, member.id)

            if robber.dinks <= 0:
                return await ctx.reply(
                    "You can't rob without dinks. Just stop being poor lol", mention_author=False, ephemeral=True
                )

            if robbed.dinks <= 0:
                return await ctx.reply(
                    f"{member.display_name} doesn't have any dinks to rob.", mention_author=False, ephemeral=True
                )

            jail = await get_user_jail(session, ctx.author.id)
            if jail is not None:
                return await ctx.reply("You can't rob when in jail.", mention_author=False, ephemeral=True)

            # Here be RNG
            rob_roll = random.random()
            success_chance = rob_chance(robber.rob_level)
            success = rob_roll <= success_chance
            max_rob_amount = math.floor(random.uniform(0.20, 1.0) * rob_amount(robber.rob_level))
            robbed_amount = min(robbed.dinks, max_rob_amount)

            if success:
                await crud.rob(session, robbed_amount, ctx.author.id, member.id, robber_bank=robber, robbed_bank=robbed)
                return await ctx.reply(
                    f"{ctx.author.display_name} has robbed **{robbed_amount}** Didier Dinks from {member.display_name}!",
                    mention_author=False,
                )

            # Remove the amount of Dinks you would've stolen
            # Increase the sentence if you can't afford it
            lost_dinks = await crud.deduct_dinks(session, ctx.author.id, max_rob_amount, bank=robber)
            couldnt_afford = lost_dinks < robbed_amount
            punishment_factor = (float(max_rob_amount) / float(lost_dinks)) if couldnt_afford else 1.0
            punishment_factor = min(punishment_factor, 2)

            to_jail = couldnt_afford or random.random() <= jail_chance(robber.rob_level)
            if to_jail:
                jail_t = jail_time(robber.rob_level) * punishment_factor
                until = tz_aware_now() + timedelta(hours=jail_t)
                await imprison(session, ctx.author.id, until)

                return await ctx.reply(
                    f"Robbery attempt failed! You've lost {lost_dinks} Didier Dinks, "
                    f"and have been sent to Didier Jail until <t:{until.timestamp()}:f>"
                )

            return await ctx.reply(f"Robbery attempt failed! You've lost {lost_dinks} Didier Dinks.")

    @commands.hybrid_command(name="jail")
    async def jail(self, ctx: commands.Context):
        """Check how long you're still in jail for"""
        async with ctx.typing():
            async with self.client.postgres_session as session:
                entry = await get_user_jail(session, ctx.author.id)

            if entry is None:
                embed = discord.Embed(
                    title="Didier Jail", colour=colours.error_red(), description="You're not currently in jail."
                )

                return await ctx.reply(embed=embed, mention_author=False, ephemeral=True)

            embed = discord.Embed(
                title="Didier Jail",
                colour=colours.jail_gray(),
                description=f"You will be released <t:{entry.until.timestamp()}:R>.",
            )

            return await ctx.reply(embed=embed, mention_author=False)


async def setup(client: Didier):
    """Load the cog"""
    await client.add_cog(Currency(client))
