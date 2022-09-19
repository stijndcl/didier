import inspect
import os
from typing import Optional

from discord.ext import commands

from didier import Didier


class Meta(commands.Cog):
    """Commands related to Didier himself."""

    client: Didier

    def __init__(self, client: Didier):
        self.client = client

    @commands.command(name="marco")
    async def marco(self, ctx: commands.Context):
        """Get Didier's latency."""
        return await ctx.reply(f"Polo! {round(self.client.latency * 1000)}ms", mention_author=False)

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

        if command_name == "help":
            command = self.client.help_command
            src = type(self.client.help_command)
            filename = inspect.getsourcefile(src)
        else:
            command = self.client.get_command(command_name)
            src = command.callback.__code__
            filename = src.co_filename

        if command is None:
            return await ctx.reply(f"Found no command named `{command_name}`.", mention_author=False)

        lines, first_line = inspect.getsourcelines(src)

        if filename is None:
            return await ctx.reply(f"Found no source file for `{command_name}`.", mention_author=False)

        file_location = os.path.relpath(filename).replace("\\", "/")

        github_url = f"{repo_home}/blob/master/{file_location}#L{first_line}-L{first_line + len(lines) - 1}"
        await ctx.reply(github_url, mention_author=False)


async def setup(client: Didier):
    """Load the cog"""
    await client.add_cog(Meta(client))
