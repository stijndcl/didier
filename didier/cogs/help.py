from typing import Mapping, Optional, List, Any

import discord
from discord.ext import commands

from didier import Didier


class CustomHelpCommand(commands.MinimalHelpCommand):
    """Customised Help command to override the default implementation
    The default is ugly as hell
    """

    client: Didier

    def __init__(self, client: Didier, **kwargs):
        super().__init__(**kwargs)
        self.client = client

    def _help_embed_base(self, title: str) -> discord.Embed:
        """Create the base structure for the embeds that get sent with the Help commands"""
        embed = discord.Embed(colour=discord.Colour.blue())
        embed.set_author(name=title)
        embed.set_footer(text="Syntax: Didier Help [Categorie] of Didier Help [Commando]")
        return embed

    async def send_bot_help(self, mapping: Mapping[Optional[commands.Cog], List[commands.Command[Any, ..., Any]]], /):
        embed = self._help_embed_base("Categorieën")

        categories = list(mapping.keys())
        print(categories)


class Help(commands.Cog):
    """Cog housing the custom Help command"""

    client: Didier

    def __init__(self, client: Didier):
        super().__init__()
        self.client = client
        self.client.help_command = CustomHelpCommand(self.client)
        self.client.help_command.cog = self
