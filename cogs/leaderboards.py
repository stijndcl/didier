from typing import Callable, Optional

from data.menus import paginated_leaderboard
from decorators import help
import discord
from discord.ext import commands
from enums.help_categories import Category
from enums.numbers import Numbers
from functions import checks, xp
from functions.database import currency, stats, poke, muttn
import math
import requests


# TODO some sort of general leaderboard generation because all of them are the same
class Leaderboards(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.utilsCog = self.client.get_cog("Utils")

    # Don't allow any commands to work when locked
    def cog_check(self, ctx):
        return not self.client.locked

    def _generate_embed_data(self, entries: list,
                             key_f: Callable = lambda x: x[0],
                             data_f: Callable = lambda x: x[1],
                             ignore_non_pos: bool = True) -> Optional[list[tuple]]:
        data = []
        for i, v in enumerate(sorted(entries, key=data_f, reverse=True)):
            entry_data = data_f(v)

            # Leaderboard is empty
            if i == 0 and entry_data == 0 and ignore_non_pos:
                return None

            # Ignore entries with no data
            if ignore_non_pos and entry_data <= 0:
                continue

            data.append((key_f(v), f"{entry_data:,}", entry_data,))

        return data

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

        data = self._generate_embed_data(entries, key_f=lambda x: x[0], data_f=lambda x: (float(x[1]) + float(x[3])))

        if data is None:
            return await self.empty_leaderboard(ctx, "Dinks Leaderboard",
                                                "Er zijn nog geen personen met Didier Dinks.")

        lb = paginated_leaderboard.Leaderboard(
            ctx=ctx, title="Dinks Leaderboard", data=data, fetch_names=True
        )

        await lb.send(ctx)

    @leaderboard.command(name="Corona", hidden=True)
    async def corona(self, ctx):
        result = requests.get("https://disease.sh/v3/covid-19/countries").json()
        result.sort(key=lambda x: int(x["cases"]), reverse=True)

        data = []
        for country in result:
            data.append((country["country"], f"{country['cases']:,}",))

        lb = paginated_leaderboard.Leaderboard(
            ctx=ctx, title="Corona Leaderboard", data=data, highlight="Belgium",
            colour=discord.Colour.red()
        )

        await lb.send(ctx)

    @leaderboard.command(name="Bitcoin", aliases=["Bc"], hidden=True)
    async def bitcoin(self, ctx):
        users = currency.getAllRows()
        data = self._generate_embed_data(users, data_f=lambda x: round(float(x[8]), 8))

        if data is None:
            return await self.empty_leaderboard(ctx, "Bitcoin Leaderboard",
                                                "Er zijn nog geen personen met Bitcoins.")

        lb = paginated_leaderboard.Leaderboard(
            ctx=ctx, title="Bitcoin Leaderboard", data=data, fetch_names=True
        )

        await lb.send(ctx)

    @leaderboard.command(name="Rob", hidden=True)
    async def rob(self, ctx):
        users = list(stats.getAllRows())
        data = self._generate_embed_data(users, data_f=lambda x: math.floor(float(x[4])))

        if data is None:
            return await self.empty_leaderboard(ctx, "Rob Leaderboard",
                                                "Er heeft nog niemand Didier Dinks gestolen.")

        lb = paginated_leaderboard.Leaderboard(
            ctx=ctx, title="Rob Leaderboard", data=data, fetch_names=True
        )

        await lb.send(ctx)

    @leaderboard.command(name="Poke", hidden=True)
    async def poke(self, ctx):
        entries = stats.getAllRows()
        blacklist = poke.getAllBlacklistedUsers()
        # Remove blacklisted users
        entries = list(filter(lambda x: x[0] not in blacklist, entries))

        data = self._generate_embed_data(entries, data_f=lambda x: round(int(x[1])))
        if data is None:
            return await self.empty_leaderboard(ctx, "Poke Leaderboard", "Er is nog niemand getikt.")

        lb = paginated_leaderboard.Leaderboard(
            ctx=ctx, title="Poke Leaderboard", data=data, fetch_names=True
        )

        await lb.send(ctx)

    @leaderboard.command(name="Xp", aliases=["Level"], hidden=True)
    async def xp(self, ctx):
        entries = stats.getAllRows()
        data = self._generate_embed_data(entries, data_f=lambda x: round(int(x[12])))

        def _format_entry(entry: int) -> str:
            return f"Level {xp.calculate_level(entry):,} | {entry:,} XP"

        lb = paginated_leaderboard.Leaderboard(
            ctx=ctx, title="XP Leaderboard", data=data, fetch_names=True, format_f=_format_entry
        )

        await lb.send(ctx)

    @leaderboard.command(name="Messages", aliases=["Mc", "Mess"], hidden=True)
    async def messages(self, ctx):
        entries = stats.getAllRows()
        message_count = stats.getTotalMessageCount()

        data = self._generate_embed_data(entries, data_f=lambda x: round(int(x[11])))

        def _format_entry(entry: int) -> str:
            perc = round(entry * 100 / message_count, 2)
            return f"{entry:,} | {perc}%"

        lb = paginated_leaderboard.Leaderboard(
            ctx=ctx, title="Messages Leaderboard", data=data, fetch_names=True, format_f=_format_entry
        )

        await lb.send(ctx)

    @leaderboard.command(name="Muttn", aliases=["M", "Mutn", "Mutten"], hidden=True)
    async def muttn(self, ctx):
        entries = muttn.getAllRows()
        data = self._generate_embed_data(entries, data_f=lambda x: round(float(x[1]), 2))
        if data is None:
            return await self.empty_leaderboard(ctx, "Muttn Leaderboard", "Der zittn nog geen muttns in de server.")

        def _format_entry(entry: float) -> str:
            return f"{entry}%"

        lb = paginated_leaderboard.Leaderboard(
            ctx=ctx, title="Muttn Leaderboard", data=data, fetch_names=True, format_f=_format_entry
        )

        await lb.send(ctx)

    async def callLeaderboard(self, name, ctx):
        command = [command for command in self.leaderboard.commands if command.name.lower() == name.lower()][0]
        await command(ctx)

    async def startPaginated(self, ctx, source, name, colour=discord.Colour.blue()):
        pages = paginated_leaderboard.Pages(source=paginated_leaderboard.Source(source, name, colour),
                                            clear_reactions_after=True)
        await pages.start(ctx)

    async def empty_leaderboard(self, ctx, name, message, colour=discord.Colour.blue()):
        embed = discord.Embed(colour=colour)
        embed.set_author(name=name)
        embed.description = message
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Leaderboards(client))
