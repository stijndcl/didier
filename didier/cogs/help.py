import inspect
import re
from typing import Mapping, Optional, Type

import discord
from discord.ext import commands
from overrides import overrides

from didier import Didier
from didier.utils.discord.colours import error_red
from didier.utils.discord.flags import PosixFlags
from didier.utils.types.string import re_find_all, re_replace_with_list


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
    def get_command_signature(self, command: commands.Command, /) -> str:
        signature_list = [command.name]

        # Perform renaming for hybrid commands
        if hasattr(command.callback, "__discord_app_commands_param_rename__"):
            renames = command.callback.__discord_app_commands_param_rename__
        else:
            renames = {}

        sig = command.params

        for name, param in sig.items():
            name = renames.get(name, name)
            is_optional = param.default is not param.empty

            # Wrap optional arguments in square brackets
            if is_optional:
                name = f"[{name}]"

            # If there are options/flags, add them
            # The hardcoded name-check is done for performance reasons
            if name == "flags" and inspect.isclass(param.annotation) and issubclass(param.annotation, PosixFlags):
                signature_list.append("[--OPTIONS]")
            else:
                signature_list.append(name)

        return " ".join(signature_list)

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

    def _clean_command_doc(self, command: commands.Command) -> str:
        """Clean up a help docstring

        This will strip out single newlines, because these are only there for readability and line length.
        These are instead replaced with spaces.

        Code in codeblocks is ignored, as it is used to create examples.
        """
        description = command.help
        codeblocks = re_find_all(r"\n?```.*?```", description, flags=re.DOTALL)

        # Regex borrowed from https://stackoverflow.com/a/59843498/13568999
        description = re.sub(
            r"([^\S\n]*\n(?:[^\S\n]*\n)+[^\S\n]*)|[^\S\n]*\n[^\S\n]*", lambda x: x.group(1) or " ", description
        )

        # Replace codeblocks with their original form
        if codeblocks:
            description = re_replace_with_list(r"```.*?```", description, codeblocks)

        # Add flag help in
        flags_class = self._get_flags_class(command)
        if flags_class is not None:
            description += f"\n\n{self.get_flags_help(flags_class)}"

        return description

    def _add_command_help(self, embed: discord.Embed, command: commands.Command):
        """Add command-related information to an embed

        This allows re-using this logic for Group commands that can be invoked by themselves.
        """
        embed.description = self._clean_command_doc(command)

        signature = self.get_command_signature(command)
        embed.add_field(name="Signature", value=signature, inline=False)

        if command.aliases:
            embed.add_field(name="Aliases", value=", ".join(sorted(command.aliases)), inline=False)

    def _get_cog(self, cogs: list[commands.Cog], name: str) -> Optional[commands.Cog]:
        """Try to find a cog, case-insensitively"""
        for cog in cogs:
            if cog.qualified_name.lower() == name:
                return cog

        return None

    async def _filter_cogs(self, cogs: list[commands.Cog]) -> list[commands.Cog]:
        """Filter the list of cogs down to all those that the user can see"""

        async def _predicate(cog: Optional[commands.Cog]) -> bool:
            if cog is None:
                return False

            # Remove cogs that we never want to see in the help page because they
            # don't contain commands, or shouldn't be visible at all
            if not cog.get_commands():
                return False

            if cog.qualified_name.lower() in ("tasks", "debugcog"):
                return False

            # Hide owner-only cogs if you're not the owner
            if not await self.context.bot.is_owner(self.context.author):
                return cog.qualified_name.lower() not in ("owner",)

            return True

        # Filter list of cogs down
        filtered_cogs = [cog for cog in cogs if await _predicate(cog)]
        return list(sorted(filtered_cogs, key=lambda cog: cog.qualified_name))

    def _get_flags_class(self, command: commands.Command) -> Optional[Type[PosixFlags]]:
        """Check if a command has flags"""
        flag_param = command.params.get("flags", None)
        if flag_param is None:
            return None

        if issubclass(flag_param.annotation, PosixFlags):
            return flag_param.annotation

        return None

    def get_flags_help(self, flags_class: Type[PosixFlags]) -> str:
        """Get the description for flag arguments"""
        help_data = []

        # Present flags in alphabetical order, as dicts have no set ordering
        flag_mapping = flags_class.__commands_flags__
        flags = list(flag_mapping.items())
        flags.sort(key=lambda f: f[0])

        for name, flag in flags:
            flag_names = [name, *flag.aliases]
            # Add the --prefix in front of all flags
            flag_names = list(map(lambda n: f"--{n}", flag_names))
            help_data.append(f"{', '.join(flag_names)} [default `{flag.default}`]")

        return "Options:\n" + "\n".join(help_data)


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
