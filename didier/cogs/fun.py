import shlex

import discord
from discord import app_commands
from discord.ext import commands

from database.crud.dad_jokes import get_random_dad_joke
from database.crud.memes import get_meme_by_name
from didier import Didier
from didier.data.apis.imgflip import generate_meme
from didier.views.modals import GenerateMeme


class Fun(commands.Cog):
    """Cog with lots of random fun stuff"""

    client: Didier

    # Slash groups
    memes_slash = app_commands.Group(name="meme", description="Commands to generate memes", guild_only=False)

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
    async def memegen_msg(self, ctx: commands.Context, meme_name: str, *, fields: str):
        """Command group for meme-related commands"""
        async with ctx.typing():
            async with self.client.postgres_session as session:
                result = await get_meme_by_name(session, meme_name)

            if result is None:
                return await ctx.reply(f"Found no meme matching `{meme_name}`.", mention_author=False)

            meme = await generate_meme(self.client.http_session, result, shlex.split(fields))
            if meme is None:
                return await ctx.reply("Something went wrong.", mention_author=False)

            return await ctx.reply(meme)

    @memes_slash.command(name="generate", description="Generate a meme")
    async def memegen_slash(self, interaction: discord.Interaction, meme: str):
        """Slash command to generate a meme"""
        async with self.client.postgres_session as session:
            result = await get_meme_by_name(session, meme)

        if result is None:
            return await interaction.response.send_message(f"Found no meme matching `{meme}`.", ephemeral=True)

        modal = GenerateMeme(self.client, result)
        await interaction.response.send_modal(modal)

    @memegen_slash.autocomplete("meme")
    async def _memegen_slash_autocomplete_meme(
        self, _: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        """Autocompletion for the 'meme'-parameter"""
        return self.client.database_caches.memes.get_autocomplete_suggestions(current)


async def setup(client: Didier):
    """Load the cog"""
    await client.add_cog(Fun(client))
