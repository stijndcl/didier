import shlex
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from database.crud.dad_jokes import get_random_dad_joke
from database.crud.memes import get_all_memes, get_meme_by_name
from didier import Didier
from didier.data.apis.imgflip import generate_meme
from didier.exceptions.no_match import expect
from didier.menus.memes import MemeSource
from didier.views.modals import GenerateMeme


class Fun(commands.Cog):
    """Cog with lots of random fun stuff"""

    client: Didier

    # Slash groups
    memes_slash = app_commands.Group(name="meme", description="Commands to generate memes.", guild_only=False)

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
    )
    async def dad_joke(self, ctx: commands.Context):
        """Why does Yoda's code always crash? Because there is no try."""
        async with self.client.postgres_session as session:
            joke = await get_random_dad_joke(session)
            return await ctx.reply(joke.joke, mention_author=False)

    @commands.group(name="memegen", aliases=["meme", "memes"], invoke_without_command=True, case_insensitive=True)
    async def memegen_msg(self, ctx: commands.Context, template: Optional[str] = None, *, fields: Optional[str] = None):
        """Generate a meme with template `template` and fields `fields`.

        The arguments are parsed based on spaces. Arguments that contain spaces should be wrapped in "quotes".

        Example: `memegen a b c d` will be parsed as `template: "a"`, `fields: ["b", "c", "d"]`

        Example: `memegen "a b" "c d"` will be parsed as `template: "a b"`, `fields: ["c d"]`

        In case a template only has 1 field, quotes aren't required and your arguments will be combined into one field.

        Example: if template `a` only has 1 field,
        `memegen a b c d` will be parsed as `template: "a"`, `fields: ["bcd"]`

        When no arguments are provided, this is a shortcut to `memegen list`.

        When only a template is provided, this is a shortcut to `memegen preview`.
        """
        if template is None:
            return await self.memegen_ls_msg(ctx)

        if fields is None:
            return await self.memegen_preview_msg(ctx, template)

        async with ctx.typing():
            meme = await self._do_generate_meme(template, shlex.split(fields))
            return await ctx.reply(meme, mention_author=False)

    @memegen_msg.command(name="list", aliases=["ls"])
    async def memegen_ls_msg(self, ctx: commands.Context):
        """Get a list of all available meme templates.

        This command does _not_ have a /slash variant, as the memegen /slash commands provide autocompletion.
        """
        async with self.client.postgres_session as session:
            results = await get_all_memes(session)

        await MemeSource(ctx, results).start()

    @memegen_msg.command(name="preview", aliases=["p"])
    async def memegen_preview_msg(self, ctx: commands.Context, template: str):
        """Generate a preview for the meme template `template`, to see how the fields are structured."""
        async with ctx.typing():
            fields = [f"Field #{i + 1}" for i in range(20)]
            meme = await self._do_generate_meme(template, fields)
            return await ctx.reply(meme, mention_author=False)

    @memes_slash.command(name="generate")
    async def memegen_slash(self, interaction: discord.Interaction, template: str):
        """Generate a meme."""
        async with self.client.postgres_session as session:
            result = expect(await get_meme_by_name(session, template), entity_type="meme", argument=template)

        modal = GenerateMeme(self.client, result)
        await interaction.response.send_modal(modal)

    @memes_slash.command(name="preview")
    @app_commands.describe(template="The meme template to use in the preview.")
    async def memegen_preview_slash(self, interaction: discord.Interaction, template: str):
        """Generate a preview for a meme, to see how the fields are structured."""
        await interaction.response.defer()

        fields = [f"Field #{i + 1}" for i in range(20)]
        meme_url = await self._do_generate_meme(template, fields)

        await interaction.followup.send(meme_url, ephemeral=True)

    @memegen_slash.autocomplete("template")
    @memegen_preview_slash.autocomplete("template")
    async def _memegen_slash_autocomplete_template(
        self, _: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        """Autocompletion for the 'template'-parameter"""
        return self.client.database_caches.memes.get_autocomplete_suggestions(current)


async def setup(client: Didier):
    """Load the cog"""
    await client.add_cog(Fun(client))
