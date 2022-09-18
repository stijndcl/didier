from typing import Mapping, Optional

import discord
from discord.ext import commands
from overrides import overrides

from didier import Didier
from didier.utils.discord.colours import error_red


class CustomHelpCommand(commands.MinimalHelpCommand):
    """Customised Help command that overrides the default implementation

    The default is ugly as hell, so we do some fiddling with it and put everything
    in fancy embeds
    """

    @overrides
    async def command_callback(self, ctx: commands.Context, /, *, command: Optional[str] = None):
        """Slightly modify the original command_callback to better suit my needs"""

        # No argument provided: send a list of all cogs
        if command is None:
            mapping = self.get_bot_mapping()
            return await self.send_bot_help(mapping)

        command = command.lower()

        # Hide cogs the user is not allowed to see
        cogs = list(ctx.bot.cogs.values())
        cogs = await self._filter_cogs(cogs)
        # Allow fetching cogs case-insensitively
        cog = self._get_cog(cogs, command)
        if cog is not None:
            return await self.send_cog_help(cog)

        # Traverse tree of commands
        keys = command.split(" ")
        current_command = ctx.bot.all_commands.get(keys[0])

        # No command found
        if current_command is None:
            return await self.send_error_message(self.command_not_found(keys[0]))

        # Look for subcommands
        for key in keys[1:]:
            try:
                found = current_command.all_commands.get(key)  # type: ignore
            except AttributeError:
                return await self.send_error_message(self.subcommand_not_found(current_command, key))
            else:
                if found is None:
                    return await self.send_error_message(self.subcommand_not_found(current_command, key))

                current_command = found

        if isinstance(current_command, commands.Group):
            return await self.send_group_help(current_command)
        else:
            return await self.send_command_help(current_command)

    @overrides
    def command_not_found(self, string: str, /) -> str:
        return f"Found no command named `{string}`."

    @overrides
    async def send_bot_help(self, mapping: Mapping[Optional[commands.Cog], list[commands.Command]], /):
        embed = self._help_embed_base("Categories")
        filtered_cogs = await self._filter_cogs(list(mapping.keys()))
        embed.description = "\n".join(list(map(lambda cog: cog.qualified_name, filtered_cogs)))
        await self.context.reply(embed=embed, mention_author=False)

    @overrides
    async def send_cog_help(self, cog: commands.Cog, /):
        embed = self._help_embed_base(cog.qualified_name)
        embed.description = cog.description

        commands_names = list(map(lambda c: c.qualified_name, cog.get_commands()))
        commands_names.sort()

        embed.add_field(name="Commands", value=", ".join(commands_names), inline=False)

        return await self.context.reply(embed=embed, mention_author=False)

    @overrides
    async def send_command_help(self, command: commands.Command, /):
        embed = self._help_embed_base(command.qualified_name)
        self._add_command_help(embed, command)

        return await self.context.reply(embed=embed, mention_author=False)

    @overrides
    async def send_group_help(self, group: commands.Group, /):
        embed = self._help_embed_base(group.qualified_name)

        if group.invoke_without_command:
            self._add_command_help(embed, group)

        subcommand_names = list(map(lambda c: c.name, group.commands))
        subcommand_names.sort()

        embed.add_field(name="Subcommands", value=", ".join(subcommand_names))

        return await self.context.reply(embed=embed, mention_author=False)

    @overrides
    async def send_error_message(self, error: str, /):
        embed = discord.Embed(colour=error_red(), title="Help", description=error)
        return await self.context.reply(embed=embed, mention_author=False)

    @overrides
    def subcommand_not_found(self, command: commands.Command, string: str, /) -> str:
        return f"Found no subcommand named `{string}` for command `{command.qualified_name}`."

    def _help_embed_base(self, title: str) -> discord.Embed:
        """Create the base structure for the embeds that get sent with the Help commands"""
        embed = discord.Embed(title=title.title(), colour=discord.Colour.blue())
        return embed

    def _add_command_help(self, embed: discord.Embed, command: commands.Command):
        """Add command-related information to an embed

        This allows re-using this logic for Group commands that can be invoked by themselves.
        """
        embed.description = command.help

        if command.usage:
            embed.add_field(name="Signature", value=f"{command.name} {command.usage}", inline=False)

        if command.aliases:
            embed.add_field(name="Aliases", value=", ".join(command.aliases), inline=False)

    def _get_cog(self, cogs: list[commands.Cog], name: str) -> Optional[commands.Cog]:
        """Try to find a cog, case-insensitively"""
        for cog in cogs:
            if cog.qualified_name.lower() == name:
                return cog

        return None

    async def _filter_cogs(self, cogs: list[commands.Cog]) -> list[commands.Cog]:
        """Filter the list of cogs down to all those that the user can see"""
        # Remove cogs that we never want to see in the help page because they
        # don't contain commands
        filtered_cogs = list(
            filter(lambda cog: cog is not None and cog.qualified_name.lower() not in ("tasks", "debugcog"), cogs)
        )

        # Remove owner-only cogs for people that shouldn't see them
        if not await self.context.bot.is_owner(self.context.author):
            filtered_cogs = list(filter(lambda cog: cog.qualified_name.lower() not in ("owner",), filtered_cogs))

        return list(sorted(filtered_cogs, key=lambda cog: cog.qualified_name))


async def setup(client: Didier):
    """Load the cog"""
    help_str = (
        "Shows the help page for a category or command. "
        "`/commands` are not included, as they already have built-in descriptions in the UI."
        "\n\nThe command signatures follow the POSIX-standard format for help messages:"
        "\n- `required_positional_argument`"
        "\n- `[optional_positional_argument]`"
    )

    attributes = {"aliases": ["h", "man"], "usage": "[category or command]", "help": help_str}

    client.help_command = CustomHelpCommand(command_attrs=attributes)
