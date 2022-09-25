import discord
from overrides import overrides

from database.schemas import Bookmark
from didier.menus.common import PageSource

__all__ = ["BookmarkSource"]

from didier.utils.discord.assets import get_author_avatar


class BookmarkSource(PageSource[Bookmark]):
    """PageSource for the Bookmark commands"""

    @overrides
    def create_embeds(self):
        for page in range(self.page_count):
            embed = discord.Embed(title="Bookmarks", colour=discord.Colour.blue())
            avatar_url = get_author_avatar(self.ctx).url
            embed.set_author(name=self.ctx.author.display_name, icon_url=avatar_url)

            description_data = []

            for bookmark in self.get_page_data(page):
                description_data.append(f"`#{bookmark.bookmark_id}`: [{bookmark.label}]({bookmark.jump_url})")

            embed.description = "\n".join(description_data)
            self.embeds.append(embed)
