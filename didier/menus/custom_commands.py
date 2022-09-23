import discord
from overrides import overrides

from database.schemas import CustomCommand
from didier.menus.common import PageSource

__all__ = ["CustomCommandSource"]


class CustomCommandSource(PageSource[CustomCommand]):
    """PageSource for custom commands"""

    @overrides
    def create_embeds(self):
        for page in range(self.page_count):
            embed = discord.Embed(colour=discord.Colour.blue(), title="Custom Commands")

            description_data = []

            for command in self.get_page_data(page):
                description_data.append(command.name.title())

            embed.description = "\n".join(description_data)
            self.embeds.append(embed)
