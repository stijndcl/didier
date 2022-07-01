from typing import Mapping, Optional, List

import discord
from discord.ext import commands

from didier import Didier


class CustomHelpCommand(commands.MinimalHelpCommand):
    """Customised Help command to override the default implementation
    The default is ugly as hell
    """

    def _help_embed_base(self, title: str) -> discord.Embed:
        """Create the base structure for the embeds that get sent with the Help commands"""
        embed = discord.Embed(colour=discord.Colour.blue())
        embed.set_author(name=title)
        embed.set_footer(text="Syntax: Didier Help [Categorie] of Didier Help [Commando]")
        return embed

    async def _filter_cogs(self, cogs: List[commands.Cog]) -> List[commands.Cog]:
        """Filter the list of cogs down to all those that the user can see"""
        # Remove cogs that we never want to see in the help page because they
        # don't contain commands
        filtered_cogs = list(filter(lambda cog: cog is not None and cog.qualified_name.lower() not in ("tasks",), cogs))

        # Remove owner-only cogs
        if not await self.context.bot.is_owner(self.context.author):
            filtered_cogs = list(filter(lambda cog: cog.qualified_name.lower() not in ("owner",), filtered_cogs))

        return list(sorted(filtered_cogs, key=lambda cog: cog.qualified_name))

    async def send_bot_help(self, mapping: Mapping[Optional[commands.Cog], List[commands.Command]], /):
        embed = self._help_embed_base("Categorieën")
        filtered_cogs = await self._filter_cogs(list(mapping.keys()))
        embed.description = "\n".join(list(map(lambda cog: cog.qualified_name, filtered_cogs)))
        await self.get_destination().send(embed=embed)


async def setup(client: Didier):
    """Load the cog"""
    client.help_command = CustomHelpCommand()
