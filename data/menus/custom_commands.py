import discord
from discord.ext import menus


# TODO rework pagination
class CommandsList(menus.ListPageSource):
    def __init__(self, data, colour=discord.Colour.blue()):
        super().__init__(data, per_page=15)
        self.colour = colour

    async def format_page(self, menu: menus.MenuPages, entries):
        embed = discord.Embed(colour=self.colour)
        embed.set_author(name="Custom Commands")
        embed.description = "\n".join(entries)
        embed.set_footer(text="{}/{}".format(menu.current_page + 1, self.get_max_pages()))

        return embed


class Pages(menus.MenuPages):
    def __init__(self, source, clear_reactions_after, timeout=30.0):
        super().__init__(source, timeout=timeout, delete_message_after=True, clear_reactions_after=clear_reactions_after)
