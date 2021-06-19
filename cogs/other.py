from discord.ext import commands
from data.menus import custom_commands
from decorators import help
from enums.help_categories import Category
from functions.database.custom_commands import get_all
from functions.stringFormatters import capitalize


class Other(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Don't allow any commands to work when locked
    def cog_check(self, ctx):
        return not self.client.locked

    @commands.command(name="Custom")
    @help.Category(category=Category.Didier)
    async def list_custom(self, ctx):
        """
        Get a list of all custom commands
        """
        all_commands = get_all()
        formatted = list(sorted(map(lambda x: capitalize(x["name"]), all_commands)))
        src = custom_commands.CommandsList(formatted)
        await custom_commands.Pages(source=src, clear_reactions_after=True).start(ctx)


def setup(client):
    client.add_cog(Other(client))
