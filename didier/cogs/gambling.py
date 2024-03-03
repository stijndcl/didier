import random
from typing import Annotated, Optional, Union

from discord.ext import commands

from database.crud.cf_stats import update_cf_stats
from database.crud.currency import gamble_dinks
from didier import Didier
from didier.utils.discord.converters import abbreviated_number
from didier.utils.types.string import pluralize


class Gambling(commands.Cog):
    """Cog for various games"""

    client: Didier

    def __init__(self, client: Didier):
        self.client = client

    @commands.max_concurrency(1, commands.BucketType.user, wait=True)
    @commands.command(name="coinflip", aliases=["cf", "flip"])  # type: ignore[arg-type]
    async def coinflip(
        self,
        ctx: commands.Context,
        amount: Optional[Annotated[Union[str, int], abbreviated_number]] = None,
        guess: Optional[str] = None,
    ):
        """Toss a coin, optionally wagering some Didier Dinks.

        Passing an argument for `amount` but not `guess` will cause the guess to be randomized.
        """
        result: str = random.choice(["heads", "tails"])

        # No stakes
        if amount is None:
            return await ctx.reply(f"{result.capitalize()}!", mention_author=False)

        if guess is None:
            guess = random.choice(["heads", "tails"])

        guess = guess.lower()

        if guess not in (
            "h",
            "heads",
            "t",
            "tails",
        ):
            return await ctx.reply('Guess must be one of "h", "heads", "t" or "tails".', mention_author=False)

        if isinstance(amount, int) and amount <= 0:
            return await ctx.reply(
                "Amount of Didier Dinks to wager must be a strictly positive integer.", mention_author=False
            )

        won = guess[0] == result[0]

        async with self.client.postgres_session as session:
            received = await gamble_dinks(session, ctx.author.id, amount, 2, won)

            if received == 0:
                return await ctx.reply("You don't have any Didier Dinks to wager.", mention_author=False)

            sign = 1 if won else -1
            await update_cf_stats(session, ctx.author.id, received * sign)

        plural = pluralize("Didier Dink", received)

        if won:
            await ctx.reply(f"{result.capitalize()}! You won **{received}** {plural}!", mention_author=False)
        else:
            await ctx.reply(f"{result.capitalize()}! You lost **{received}** {plural}!", mention_author=False)


async def setup(client: Didier):
    """Load the cog"""
    await client.add_cog(Gambling(client))
