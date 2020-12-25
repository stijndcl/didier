from data import paginatedLeaderboard
from decorators import help
import discord
from discord.ext import commands
from enums.help_categories import Category
from enums.numbers import Numbers
from functions import checks, xp
from functions.database import currency, stats, poke, muttn
import math
import requests


# TODO some sort of general leaderboard because all of them are the same
class Leaderboards(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.utilsCog = self.client.get_cog("Utils")

    # Don't allow any commands to work when locked
    def cog_check(self, ctx):
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
        entries = currency.getAllRows()
        platDinks = currency.getAllPlatDinks()

        # Take platinum dinks into account
        for i, user in enumerate(entries):
            if str(user[0]) in platDinks:
                # Tuples don't support assignment, cast to list
                user = list(user)
                user[1] += platDinks[str(user[0])] * Numbers.q.value
                entries[i] = user

        boardTop = []
        for i, user in enumerate(sorted(entries, key=lambda x: (float(x[1]) + float(x[3])), reverse=True)):
            if i == 0 and float(user[1]) + float(user[3]) == 0.0:
                return await self.emptyLeaderboard(ctx, "Dinks Leaderboard", "Er zijn nog geen personen met Didier Dinks.")
            elif float(user[1]) + float(user[3]) > 0.0:

                # Get the username in this guild
                name = self.utilsCog.getDisplayName(ctx, user[0])

                if int(user[0]) == int(ctx.author.id):
                    boardTop.append("**{} ({:,})**".format(name, math.floor(float(user[1]) + float(user[3]))))
                else:
                    boardTop.append("{} ({:,})".format(name, math.floor(float(user[1]) + float(user[3]))))

        await self.startPaginated(ctx, boardTop, "Dinks Leaderboard")

    @leaderboard.command(name="Corona", hidden=True)
    async def corona(self, ctx):
        result = requests.get("http://corona.lmao.ninja/v2/countries").json()
        result.sort(key=lambda x: int(x["cases"]), reverse=True)
        board = []
        for land in result:

            if land["country"] == "Belgium":
                board.append("**{} ({:,})**".format(land["country"], land["cases"]))
            else:
                board.append("{} ({:,})".format(land["country"], land["cases"]))

        await self.startPaginated(ctx, board, "Corona Leaderboard", discord.Colour.red())

    @leaderboard.command(name="Bitcoin", aliases=["Bc"], hidden=True)
    async def bitcoin(self, ctx):
        users = currency.getAllRows()
        boardTop = []
        for i, user in enumerate(sorted(users, key=lambda x: x[8], reverse=True)):
            # Don't create an empty leaderboard
            if i == 0 and float(user[8]) == 0.0:
                return await self.emptyLeaderboard(ctx, "Bitcoin Leaderboard", "Er zijn nog geen personen met Bitcoins.")
            elif float(user[8]) > 0.0:
                # Only add people with more than 0
                # Get the username in this guild
                name = self.utilsCog.getDisplayName(ctx, user[0])
                if int(user[0]) == int(ctx.author.id):
                    boardTop.append("**{} ({:,})**".format(name, round(user[8], 8)))
                else:
                    boardTop.append("{} ({:,})".format(name, round(user[8], 8)))

        await self.startPaginated(ctx, boardTop, "Bitcoin Leaderboard")

    @leaderboard.command(name="Rob", hidden=True)
    async def rob(self, ctx):
        users = list(stats.getAllRows())
        boardTop = []
        for i, user in enumerate(sorted(users, key=lambda x: x[4], reverse=True)):
            # Don't create an empty leaderboard
            if i == 0 and float(user[4]) == 0.0:
                return await self.emptyLeaderboard(ctx, "Rob Leaderboard", "Er heeft nog niemand Didier Dinks gestolen.")
            elif float(user[4]) > 0.0:
                # Only add people with more than 0
                # Get the username in this guild
                name = self.utilsCog.getDisplayName(ctx, user[0])
                if int(user[0]) == int(ctx.author.id):
                    boardTop.append("**{} ({:,})**".format(name, math.floor(float(user[4]))))
                else:
                    boardTop.append("{} ({:,})".format(name, math.floor(float(user[4]))))
        await self.startPaginated(ctx, boardTop, "Rob Leaderboard")

    @leaderboard.command(name="Poke", hidden=True)
    async def poke(self, ctx):
        s = stats.getAllRows()
        blacklist = poke.getAllBlacklistedUsers()
        boardTop = []
        for i, user in enumerate(sorted(s, key=lambda x: x[1], reverse=True)):
            if i == 0 and int(user[1]) == 0:
                return await self.emptyLeaderboard(ctx, "Poke Leaderboard", "Er is nog niemand getikt.")

            elif int(user[1]) == 0:
                break
            # Don't include blacklisted users
            elif str(user[0]) not in blacklist:
                name = self.utilsCog.getDisplayName(ctx, user[0])
                if int(user[0]) == int(ctx.author.id):
                    boardTop.append("**{} ({:,})**".format(name, round(int(user[1]))))
                else:
                    boardTop.append("{} ({:,})".format(name, round(int(user[1]))))
        await self.startPaginated(ctx, boardTop, "Poke Leaderboard")

    @leaderboard.command(name="Xp", aliases=["Level"], hidden=True)
    async def xp(self, ctx):
        s = stats.getAllRows()
        boardTop = []
        for i, user in enumerate(sorted(s, key=lambda x: x[12], reverse=True)):
            if int(user[12]) == 0:
                break

            name = self.utilsCog.getDisplayName(ctx, user[0])
            if int(user[0]) == int(ctx.author.id):
                boardTop.append("**{} (Level {:,} | {:,} XP)**".format(name,
                                                                       xp.calculate_level(round(int(user[12]))),
                                                                       round(int(user[12]))))
            else:
                boardTop.append("{} (Level {:,} | {:,} XP)".format(name,
                                                                   xp.calculate_level(round(int(user[12]))),
                                                                   round(int(user[12]))))
        await self.startPaginated(ctx, boardTop, "XP Leaderboard")

    @leaderboard.command(name="Messages", aliases=["Mc", "Mess"], hidden=True)
    async def messages(self, ctx):
        s = stats.getAllRows()
        boardTop = []

        message_count = stats.getTotalMessageCount()

        for i, user in enumerate(sorted(s, key=lambda x: x[11], reverse=True)):
            if int(user[11]) == 0:
                break

            perc = round(int(user[11]) * 100 / message_count, 2)

            name = self.utilsCog.getDisplayName(ctx, user[0])
            if int(user[0]) == int(ctx.author.id):
                boardTop.append("**{} ({:,} | {}%)**".format(name, round(int(user[11])), perc))
            else:
                boardTop.append("{} ({:,} | {}%)".format(name, round(int(user[11])), perc))
        await self.startPaginated(ctx, boardTop, "Messages Leaderboard")

    @leaderboard.command(name="Muttn", aliases=["M", "Mutn", "Mutten"], hidden=True)
    async def muttn(self, ctx):
        users = muttn.getAllRows()
        boardTop = []
        for i, user in enumerate(sorted(users, key=lambda x: x[1], reverse=True)):
            if i == 0 and int(user[1]) == 0:
                return await self.emptyLeaderboard(ctx, "Muttn Leaderboard", "Der zittn nog geen muttns in de server.")

            if float(user[1]) == 0:
                break

            name = self.utilsCog.getDisplayName(ctx, user[0])
            if int(user[0]) == int(ctx.author.id):
                boardTop.append("**{} ({})%**".format(name, round(float(user[1]), 2)))
            else:
                boardTop.append("{} ({}%)".format(name, round(float(user[1]), 2)))
        await self.startPaginated(ctx, boardTop, "Muttn Leaderboard")

    async def callLeaderboard(self, name, ctx):
        await [command for command in self.leaderboard.commands if command.name.lower() == name.lower()][0](ctx)

    async def startPaginated(self, ctx, source, name, colour=discord.Colour.blue()):
        pages = paginatedLeaderboard.Pages(source=paginatedLeaderboard.Source(source, name, colour),
                                           clear_reactions_after=True)
        await pages.start(ctx)

    async def emptyLeaderboard(self, ctx, name, message, colour=discord.Colour.blue()):
        embed = discord.Embed(colour=colour)
        embed.set_author(name=name)
        embed.description = message
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Leaderboards(client))
