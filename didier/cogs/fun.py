import shlex

import discord
from discord import app_commands
from discord.ext import commands

from database.crud.dad_jokes import get_random_dad_joke
from database.crud.memes import get_meme_by_name
from didier import Didier
from didier.data.apis.imgflip import generate_meme
from didier.exceptions.no_match import expect
from didier.views.modals import GenerateMeme


class Fun(commands.Cog):
    """Cog with lots of random fun stuff"""

    client: Didier

    # Slash groups
    memes_slash = app_commands.Group(name="meme", description="Commands to generate memes", guild_only=False)

    def __init__(self, client: Didier):
        self.client = client

    async def _do_generate_meme(self, meme_name: str, fields: list[str]) -> str:
        async with self.client.postgres_session as session:
            result = expect(await get_meme_by_name(session, meme_name), entity_type="meme", argument=meme_name)
            meme = await generate_meme(self.client.http_session, result, fields)
            return meme

    @commands.hybrid_command(
        name="dadjoke",
        aliases=["dad", "dj"],
        description="Why does Yoda's code always crash? Because there is no try.",
    )
    async def dad_joke(self, ctx: commands.Context):
        """Get a random dad joke"""
        async with self.client.postgres_session as session:
            joke = await get_random_dad_joke(session)
            return await ctx.reply(joke.joke, mention_author=False)

    @commands.group(name="memegen", aliases=["meme", "memes"], invoke_without_command=True, case_insensitive=True)
    async def memegen_msg(self, ctx: commands.Context, meme_name: str, *, fields: str):
        """Command group for meme-related commands"""
        async with ctx.typing():
            meme = await self._do_generate_meme(meme_name, shlex.split(fields))
            return await ctx.reply(meme, mention_author=False)

    @memegen_msg.command(name="preview", aliases=["p"])
    async def memegen_preview_msg(self, ctx: commands.Context, meme_name: str):
        """Generate a preview for a meme, to see how the fields are structured"""
        async with ctx.typing():
            fields = [f"Field #{i + 1}" for i in range(20)]
            meme = await self._do_generate_meme(meme_name, fields)
            return await ctx.reply(meme, mention_author=False)

    @memes_slash.command(name="generate", description="Generate a meme")
    async def memegen_slash(self, interaction: discord.Interaction, meme: str):
        """Slash command to generate a meme"""
        async with self.client.postgres_session as session:
            result = expect(await get_meme_by_name(session, meme), entity_type="meme", argument=meme)

        modal = GenerateMeme(self.client, result)
        await interaction.response.send_modal(modal)

    @memes_slash.command(
        name="preview", description="Generate a preview for a meme, to see how the fields are structured"
    )
    async def memegen_preview_slash(self, interaction: discord.Interaction, meme: str):
        """Slash command to generate a meme preview"""
        await interaction.response.defer()

        fields = [f"Field #{i + 1}" for i in range(20)]
        meme_url = await self._do_generate_meme(meme, fields)

        await interaction.followup.send(meme_url, ephemeral=True)

    @memegen_slash.autocomplete("meme")
    @memegen_preview_slash.autocomplete("meme")
    async def _memegen_slash_autocomplete_meme(
        self, _: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        """Autocompletion for the 'meme'-parameter"""
        return self.client.database_caches.memes.get_autocomplete_suggestions(current)


async def setup(client: Didier):
    """Load the cog"""
    await client.add_cog(Fun(client))
