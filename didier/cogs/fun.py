import discord
from discord import app_commands
from discord.ext import commands

from database.crud.dad_jokes import get_random_dad_joke
from didier import Didier


class Fun(commands.Cog):
    """Cog with lots of random fun stuff"""

    client: Didier

    memegen_slash = app_commands.Group(name="meme", description="Commands to generate memes")

    def __init__(self, client: Didier):
        self.client = client

    @commands.hybrid_command(
        name="dadjoke",
        aliases=["Dad", "Dj"],
        description="Why does Yoda's code always crash? Because there is no try.",
    )
    async def dad_joke(self, ctx: commands.Context):
        """Get a random dad joke"""
        async with self.client.postgres_session as session:
            joke = await get_random_dad_joke(session)
            return await ctx.reply(joke.joke, mention_author=False)

    @commands.group(name="Memegen", aliases=["Meme", "Memes"], invoke_without_command=True, case_insensitive=True)
    async def memegen_ctx(self, ctx: commands.Context):
        """Command group for meme-related commands"""

    @memegen_slash.command(name="generate", description="Generate a meme")
    async def memegen_slash(self, ctx: commands.Context, meme: str):
        """Slash command to generate a meme"""

    @memegen_slash.autocomplete("meme")
    async def _memegen_slash_autocomplete_meme(
        self, _: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        """Autocompletion for the 'meme'-parameter"""
        return self.client.database_caches.memes.get_autocomplete_suggestions(current)


async def setup(client: Didier):
    """Load the cog"""
    await client.add_cog(Fun(client))
