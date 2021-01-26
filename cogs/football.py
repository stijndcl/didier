from decorators import help
from discord.ext import commands
from enums.help_categories import Category
from functions import checks, config
from functions.football import getMatches, getTable


class Football(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Don't allow any commands to work when locked
    def cog_check(self, ctx):
        return not self.client.locked

    @commands.group(name="Jpl", case_insensitive=True, invoke_without_command=True)
    @commands.check(checks.allowedChannels)
    @help.Category(Category.Sports)
    async def jpl(self, ctx, *args):
        pass

    @jpl.command(name="Matches", aliases=["M"], usage="[Week]*")
    async def matches(self, ctx, *args):
        args = list(args)

        # Default is current day
        if not args:
            args = [str(config.get("jpl_day"))]

        if all(letter.isdigit() for letter in args[0]):
            await ctx.send(getMatches(int(args[0])))
        else:
            return await ctx.send("Dit is geen geldige speeldag.")

    @jpl.command(name="Table", aliases=["Ranking", "Rankings", "Ranks", "T"])
    async def table(self, ctx, *args):
        await ctx.send(getTable())


def setup(client):
    client.add_cog(Football(client))
