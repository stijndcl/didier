import shlex
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from database.crud.dad_jokes import get_random_dad_joke
from database.crud.memes import get_all_memes, get_meme_by_name
from didier import Didier
from didier.data.apis.imgflip import generate_meme
from didier.data.apis.xkcd import fetch_xkcd_post
from didier.exceptions.no_match import expect
from didier.menus.memes import MemeSource
from didier.utils.discord import constants
from didier.utils.types.string import mock
from didier.views.modals import GenerateMeme


class Fun(commands.Cog):
    """Cog with lots of random fun stuff"""

    client: Didier

    # Slash groups
    memes_slash = app_commands.Group(name="meme", description="Commands to generate memes.", guild_only=False)

    def __init__(self, client: Didier):
        self.client = client

    @commands.hybrid_command(name="clap")
    async def clap(self, ctx: commands.Context, *, text: str):
        """Clap a message with emojis for extra dramatic effect"""
        chars = list(filter(lambda c: c in constants.EMOJI_MAP, text))

        if not chars:
            return await ctx.reply("👏", mention_author=False)

        text = "👏".join(list(map(lambda c: constants.EMOJI_MAP[c], chars)))
        text = f"👏{text}👏"

        if len(text) > constants.Limits.MESSAGE_LENGTH:
            return await ctx.reply("Message is too long.", mention_author=False)

        return await ctx.reply(text, mention_author=False)

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
            meme = await self._do_generate_meme(template, [])
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
        await interaction.response.defer(ephemeral=True)

        meme_url = await self._do_generate_meme(template, [])

        await interaction.followup.send(meme_url, ephemeral=True)

    @memegen_slash.autocomplete("template")
    @memegen_preview_slash.autocomplete("template")
    async def _memegen_slash_autocomplete_template(
        self, _: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        """Autocompletion for the 'template'-parameter"""
        return self.client.database_caches.memes.get_autocomplete_suggestions(current)

    @app_commands.command()
    @app_commands.describe(message="The text to convert.")
    async def mock(self, interaction: discord.Interaction, message: str):
        """Mock a message.

        This returns the mocked version ephemerally so that you can copy-paste it easily,
        instead of the old version where Didier would send a public message.

        The mocked message escapes all Markdown syntax.
        """
        await interaction.response.defer(ephemeral=True)

        # Nitro users can send longer messages that Didier can't repeat back to them
        if len(message) > constants.Limits.MESSAGE_LENGTH:
            return await interaction.followup.send("That message is too long.")

        message = discord.utils.escape_markdown(message)

        # Escaping md syntax can make the message longer than the limit
        if len(message) > constants.Limits.MESSAGE_LENGTH:
            return await interaction.followup.send("Because of Markdown syntax escaping, that message is too long.")

        return await interaction.followup.send(mock(message))

    @commands.hybrid_command(name="xkcd")
    @app_commands.rename(comic_id="id")
    async def xkcd(self, ctx: commands.Context, comic_id: Optional[int] = None):
        """Fetch comic `#id` from xkcd.

        If no argument to `id` is passed, this fetches today's comic instead.
        """
        async with ctx.typing():
            post = await fetch_xkcd_post(self.client.http_session, num=comic_id)

        await ctx.reply(embed=post.to_embed(), mention_author=False, ephemeral=False)


async def setup(client: Didier):
    """Load the cog"""
    await client.add_cog(Fun(client))
