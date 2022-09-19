from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from database.crud.links import get_link_by_name
from database.schemas import Link
from didier import Didier
from didier.data.apis import urban_dictionary
from didier.data.embeds.google import GoogleSearch
from didier.data.scrapers import google


class Other(commands.Cog):
    """Commands that don't really belong anywhere else."""

    client: Didier

    def __init__(self, client: Didier):
        self.client = client

    @commands.hybrid_command(
        name="define", aliases=["ud", "urban"], description="Look up the definition of a word on the Urban Dictionary"
    )
    async def define(self, ctx: commands.Context, *, query: str):
        """Look up the definition of `query` on the Urban Dictionary."""
        async with ctx.typing():
            status_code, definitions = await urban_dictionary.lookup(self.client.http_session, query)
            if not definitions:
                return await ctx.reply(f"Something went wrong (status {status_code})")

            await ctx.reply(embed=definitions[0].to_embed(), mention_author=False)

    @commands.hybrid_command(name="google", description="Google search")
    @app_commands.describe(query="Search query")
    async def google(self, ctx: commands.Context, *, query: str):
        """Show the Google search results for `query`.

        The `query`-argument can contain spaces and does not require quotes around it. For example:
        ```
        didier query didier source github
        didier query "didier source github"
        ```
        """
        async with ctx.typing():
            results = await google.google_search(self.client.http_session, query)
            embed = GoogleSearch(results).to_embed()
            await ctx.reply(embed=embed, mention_author=False)

    async def _get_link(self, name: str) -> Optional[Link]:
        async with self.client.postgres_session as session:
            return await get_link_by_name(session, name.lower())

    @commands.command(name="Link", aliases=["Links"])
    async def link_msg(self, ctx: commands.Context, name: str):
        """Get the link to the resource named `name`."""
        link = await self._get_link(name)
        if link is None:
            return await ctx.reply(f"Found no links matching `{name}`.", mention_author=False)

        target_message = await self.client.get_reply_target(ctx)
        await target_message.reply(link.url, mention_author=False)

    @app_commands.command(name="link")
    @app_commands.describe(name="The name of the resource")
    async def link_slash(self, interaction: discord.Interaction, name: str):
        """Get the link to something."""
        link = await self._get_link(name)
        if link is None:
            return await interaction.response.send_message(f"Found no links matching `{name}`.", ephemeral=True)

        return await interaction.response.send_message(link.url)

    @link_slash.autocomplete("name")
    async def _link_name_autocomplete(self, _: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        """Autocompletion for the 'name'-parameter"""
        return self.client.database_caches.links.get_autocomplete_suggestions(current)


async def setup(client: Didier):
    """Load the cog"""
    await client.add_cog(Other(client))
