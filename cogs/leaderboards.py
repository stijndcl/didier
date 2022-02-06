import discord
from discord.ext import commands

from data.menus import leaderboards
from decorators import help
from enums.help_categories import Category
from functions import checks


class Leaderboards(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.utilsCog = self.client.get_cog("Utils")

    # Don't allow any commands to work when locked
    def cog_check(self, _):
        return not self.client.locked

    @commands.group(name="Leaderboard", aliases=["Lb", "Leaderboards"], case_insensitive=True, usage="[Categorie]*",
                    invoke_without_command=True)
    @commands.check(checks.allowedChannels)
    @help.Category(category=Category.Other)
    async def leaderboard(self, ctx):
        categories = ["Bitcoin", "Corona", "Dinks", "Messages", "Poke", "Rob", "XP"]
        embed = discord.Embed(colour=discord.Colour.blue())
        embed.set_author(name="Leaderboard Categorieën")
        embed.description = "\n".join(categories)
        await ctx.channel.send(embed=embed)

    @leaderboard.command(name="Dinks", aliases=["Cash"], hidden=True)
    async def dinks(self, ctx):
        lb = leaderboards.DinksLeaderboard(ctx=ctx)
        await lb.send()

    @leaderboard.command(name="Corona", hidden=True)
    async def corona(self, ctx):
        lb = leaderboards.CoronaLeaderboard(ctx=ctx)
        await lb.send()

    @leaderboard.command(name="Bitcoin", aliases=["Bc"], hidden=True)
    async def bitcoin(self, ctx):
        lb = leaderboards.BitcoinLeaderboard(ctx=ctx)
        await lb.send()

    @leaderboard.command(name="Rob", hidden=True)
    async def rob(self, ctx):
        lb = leaderboards.RobLeaderboard(ctx=ctx)
        await lb.send()

    @leaderboard.command(name="Poke", hidden=True)
    async def poke(self, ctx):
        lb = leaderboards.PokeLeaderboard(ctx=ctx)
        await lb.send()

    @leaderboard.command(name="Xp", aliases=["Level"], hidden=True)
    async def xp(self, ctx):
        lb = leaderboards.XPLeaderboard(ctx=ctx)
        await lb.send()

    @leaderboard.command(name="Messages", aliases=["Mc", "Mess"], hidden=True)
    async def messages(self, ctx):
        lb = leaderboards.MessageLeaderboard(ctx=ctx)
        await lb.send()

    @leaderboard.command(name="Muttn", aliases=["M", "Mutn", "Mutten"], hidden=True)
    async def muttn(self, ctx):
        lb = leaderboards.MuttnLeaderboard(ctx=ctx)
        await lb.send()

    async def callLeaderboard(self, name, ctx):
        command = [command for command in self.leaderboard.commands if command.name.lower() == name.lower()][0]
        await command(ctx)


def setup(client):
    client.add_cog(Leaderboards(client))
