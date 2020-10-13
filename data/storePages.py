import discord
from discord.ext import menus


# https://github.com/Rapptz/discord-ext-menus
class Source(menus.ListPageSource):
    def __init__(self, data):
        super().__init__(data, per_page=10)
        self.name = "Didier Store"
        self.colour = discord.Colour.blue()

    async def format_page(self, menu: menus.MenuPages, entries):
        offset = menu.current_page * self.per_page

        embed = discord.Embed(colour=self.colour)
        embed.set_author(name=self.name)
        embed.description = "Heb je een idee voor een item? DM DJ STIJN met je idee!"
        embed.set_footer(text="{}/{}".format(menu.current_page + 1, self.get_max_pages()))

        for i, v in enumerate(entries, start=offset):
            embed.add_field(name="#{} - {}".format(v[0], v[1]), value="{:,} Didier Dinks".format(v[2]))

        return embed


class Pages(menus.MenuPages):
    def __init__(self, source, clear_reactions_after, timeout=30.0):
        super().__init__(source, timeout=timeout, delete_message_after=True, clear_reactions_after=clear_reactions_after)
