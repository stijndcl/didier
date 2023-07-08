import inspect
import os
from typing import Any, Optional, Union

from discord.ext import commands

from database.crud.custom_commands import get_all_commands
from database.crud.reminders import toggle_reminder
from database.enums import ReminderCategory
from didier import Didier
from didier.menus.custom_commands import CustomCommandSource


class Meta(commands.Cog):
    """Commands related to Didier himself."""

    client: Didier

    def __init__(self, client: Didier):
        self.client = client

    @commands.command(name="custom")
    async def custom(self, ctx: commands.Context):
        """Get a list of all custom commands that are registered."""
        async with self.client.postgres_session as session:
            custom_commands = await get_all_commands(session)

        custom_commands.sort(key=lambda c: c.name.lower())
        await CustomCommandSource(ctx, custom_commands).start()

    @commands.command(name="marco")
    async def marco(self, ctx: commands.Context):
        """Get Didier's latency."""
        return await ctx.reply(f"Polo! {round(self.client.latency * 1000)}ms", mention_author=False)

    @commands.command(name="remind", aliases=["remindme"])
    async def remind(self, ctx: commands.Context, category: str):
        """Make Didier send you reminders every day."""
        category = category.lower()

        available_categories = [
            (
                "les",
                ReminderCategory.LES,
            )
        ]

        for name, category_mapping in available_categories:
            if name == category:
                async with self.client.postgres_session as session:
                    new_value = await toggle_reminder(session, ctx.author.id, category_mapping)

                toggle = "on" if new_value else "off"
                return await ctx.reply(
                    f"Reminders for category `{name}` have been toggled {toggle}.", mention_author=False
                )

        # No match found
        return await ctx.reply(f"`{category}` is not a supported category.", mention_author=False)

    @commands.command(name="source", aliases=["src"])
    async def source(self, ctx: commands.Context, *, command_name: Optional[str] = None):
        """Get a link to the source code of Didier.

        If a value for `command_name` is passed, the source for `command_name` is shown instead.

        Example usage:
        ```
        didier source
        didier source dinks
        didier source source
        ```
        """
        repo_home = "https://github.com/stijndcl/didier"

        if command_name is None:
            return await ctx.reply(repo_home, mention_author=False)

        command: Optional[Union[commands.HelpCommand, commands.Command]]
        src: Any

        if command_name == "help":
            command = self.client.help_command
            if command is None:
                return await ctx.reply(f"Found no command named `{command_name}`.", mention_author=False)

            src = type(self.client.help_command)
            filename = inspect.getsourcefile(src)
        else:
            command = self.client.get_command(command_name)
            if command is None:
                return await ctx.reply(f"Found no command named `{command_name}`.", mention_author=False)

            src = command.callback.__code__
            filename = src.co_filename

        lines, first_line = inspect.getsourcelines(src)

        if filename is None:
            return await ctx.reply(f"Found no source file for `{command_name}`.", mention_author=False)

        file_location = os.path.relpath(filename).replace("\\", "/")

        github_url = f"{repo_home}/blob/master/{file_location}#L{first_line}-L{first_line + len(lines) - 1}"
        await ctx.reply(github_url, mention_author=False)


async def setup(client: Didier):
    """Load the cog"""
    await client.add_cog(Meta(client))
