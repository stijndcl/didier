import discord
from discord.ext import commands
from overrides import overrides

from database.schemas import Bookmark
from didier.menus.common import PageSource

__all__ = ["BookmarkSource"]

from didier.utils.discord.assets import get_author_avatar


class BookmarkSource(PageSource[Bookmark]):
    """PageSource for the Bookmark commands"""

    @overrides
    def create_embeds(self, ctx: commands.Context):
        for page in range(self.page_count):
            embed = discord.Embed(title="Bookmarks", colour=discord.Colour.blue())
            avatar_url = get_author_avatar(ctx).url
            embed.set_author(name=ctx.author.display_name, icon_url=avatar_url)

            description = ""

            for bookmark in self.dataset[page : page + self.per_page]:
                description += f"`#{bookmark.bookmark_id}`: [{bookmark.label}]({bookmark.jump_url})\n"

            embed.description = description.strip()
            self.embeds.append(embed)
