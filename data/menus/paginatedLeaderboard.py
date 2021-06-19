import discord
from discord.ext import menus


# https://github.com/Rapptz/discord-ext-menus
class Source(menus.ListPageSource):
    def __init__(self, data, name, colour=discord.Colour.blue()):
        super().__init__(data, per_page=10)
        self.name = name
        self.colour = colour

    async def format_page(self, menu: menus.MenuPages, entries):
        offset = menu.current_page * self.per_page

        description = ""
        for i, v in enumerate(entries, start=offset):
            # Check if the person's name has to be highlighted
            if v.startswith("**") and v.endswith("**"):
                description += "**"
                v = v[2:]
            description += "{}: {}\n".format(i + 1, v)
        embed = discord.Embed(colour=self.colour)
        embed.set_author(name=self.name)
        embed.description = description
        embed.set_footer(text="{}/{}".format(menu.current_page + 1, self.get_max_pages()))
        return embed


class Pages(menus.MenuPages):
    def __init__(self, source, clear_reactions_after, timeout=30.0):
        super().__init__(source, timeout=timeout, delete_message_after=True, clear_reactions_after=clear_reactions_after)
