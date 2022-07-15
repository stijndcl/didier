from discord.ext import commands

from database.crud.dad_jokes import get_random_dad_joke
from didier import Didier


class Fun(commands.Cog):
    """Cog with lots of random fun stuff"""

    client: Didier

    def __init__(self, client: Didier):
        self.client = client

    @commands.hybrid_command(
        name="dadjoke",
        aliases=["Dad", "Dj"],
        description="Why does Yoda's code always crash? Because there is no try.",
    )
    async def dad_joke(self, ctx: commands.Context):
        """Get a random dad joke"""
        async with self.client.db_session as session:
            joke = await get_random_dad_joke(session)
            return await ctx.reply(joke.joke, mention_author=False)


async def setup(client: Didier):
    """Load the cog"""
    await client.add_cog(Fun(client))
