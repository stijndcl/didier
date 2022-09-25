import discord
from overrides import overrides

from database.schemas import MemeTemplate
from didier.menus.common import PageSource

__all__ = ["MemeSource"]


class MemeSource(PageSource[MemeTemplate]):
    """PageSource for meme templates"""

    @overrides
    def create_embeds(self):
        for page in range(self.page_count):
            # The colour of the embed is (69,4,20) with the values +100 because they were too dark
            embed = discord.Embed(title="Meme Templates", colour=discord.Colour.from_rgb(169, 14, 120))

            description_data = []
            for template in self.get_page_data(page):
                description_data.append(f"{template.name} ({template.field_count})")

            embed.description = "\n".join(description_data)
            embed.set_footer(text="Format: Template Name (Field Count)")

            self.embeds.append(embed)
