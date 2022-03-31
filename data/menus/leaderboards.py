import json
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Union, Optional

import discord
import requests
from discord import ApplicationContext
from discord.ext.commands import Context

import settings
from data.menus.paginated import Paginated
from enums.numbers import Numbers
from functions import xp
from functions.database import currency, stats, poke, muttn
from functions.utils import get_display_name, get_mention


@dataclass
class Leaderboard(Paginated, ABC):
    highlight: str = None
    colour: discord.Colour = discord.Colour.blue()
    fetch_names: bool = True
    ignore_non_pos: bool = True
    reverse: bool = True

    def __post_init__(self):
        self.data = self.process_data(self.get_data())

    @abstractmethod
    def get_data(self) -> list[tuple]:
        pass

    def process_data(self, entries: list[tuple]) -> Optional[list[tuple]]:
        data = []
        for i, v in enumerate(sorted(entries, key=self.get_value, reverse=self.reverse)):
            entry_data = self.get_value(v)

            # Leaderboard is empty
            if i == 0 and entry_data == 0 and self.ignore_non_pos:
                return None

            # Ignore entries with no data
            if self.ignore_non_pos and entry_data <= 0:
                continue

            data.append((self.get_key(v), f"{entry_data:,}", entry_data,))

        return data

    def get_key(self, data: tuple):
        return data[0]

    def get_value(self, data: tuple):
        return data[1]

    def _should_highlight(self, data) -> bool:
        """Check if an entry should be highlighted"""
        if self.fetch_names:
            return data == self.ctx.author.id

        return data == self.highlight

    def format_entry_data(self, data: tuple) -> str:
        return str(data[1])

    def format_entry(self, index: int, data: tuple) -> str:
        name = data[0]

        if self.fetch_names:
            name = get_display_name(self.ctx, int(data[0]))

        s = f"{index + 1}: {name} ({self.format_entry_data(data)})"

        if self._should_highlight(data[0]):
            return f"**{s}**"

        return s

    @property
    def empty_description(self) -> str:
        return ""

    async def empty_leaderboard(self, ctx: Union[ApplicationContext, Context], **kwargs):
        embed = discord.Embed(colour=self.colour)
        embed.set_author(name=self.title)
        embed.description = self.empty_description

        if isinstance(ctx, ApplicationContext):
            return await ctx.respond(embed=embed)

        return await ctx.reply(embed=embed, **kwargs)

    async def respond(self, **kwargs) -> discord.Message:
        if self.data is None or not self.data:
            return await self.empty_leaderboard(self.ctx, **kwargs)

        return await super().respond(**kwargs)

    async def send(self, **kwargs) -> discord.Message:
        if self.data is None or not self.data:
            return await self.empty_leaderboard(self.ctx, **kwargs)

        return await super().send(**kwargs)


@dataclass
class BitcoinLeaderboard(Leaderboard):
    title: str = field(default="Bitcoin Leaderboard")

    def get_data(self) -> list[tuple]:
        return currency.getAllRows()

    def get_value(self, data: tuple):
        return round(float(data[8]), 8)

    @property
    def empty_description(self) -> str:
        return "Er zijn nog geen personen met Bitcoins."


@dataclass
class CompbioLeaderboard(Leaderboard):
    colour: discord.Colour = field(default=discord.Colour.green())
    title: str = field(default="Leaderboard Computationele Biologie #4")
    reverse: bool = False
    size: int = 10000
    amount: int = 10

    def __post_init__(self):
        self.title += f" ({self.size}-{self.amount})"
        super().__post_init__()

    def get_submission_user(self, submission_id: str) -> str:
        with open("files/compbio_benchmarks_4.json", "r") as fp:
            file = json.load(fp)

        if submission_id in file:
            user_id = file[submission_id]
            return get_mention(self.ctx, user_id)

        return f"[# {submission_id}]"

    def get_data(self) -> list[tuple]:
        url = f"https://github.ugent.be/raw/computationele-biologie/benchmarks-2022/main/profile_hmm/size{self.size}-amount{self.amount}.md"
        headers = {"Authorization": f"token {settings.UGENT_GH_TOKEN}"}
        result = requests.get(url, headers=headers).text

        # Remove table headers
        result = result.split("\n")[2:]
        data = []

        for line in result:
            try:
                cells = line.split("|")
                submission_id = cells[1].strip()
                mean = float(cells[2].strip().split(" ")[0])
            except IndexError:
                # Other lines because of markdown formatting
                continue

            data.append((submission_id, mean, ))

        return data

    def _should_highlight(self, data) -> bool:
        # TODO maybe find a fix for this?
        return False

    def format_entry(self, index: int, data: tuple) -> str:
        return f"{index + 1}: {self.get_submission_user(data[0])} ({self.format_entry_data(data)})"

    def format_entry_data(self, data: tuple) -> str:
        return f"{str(data[1])} s"

    def get_value(self, data: tuple):
        return data[1]


@dataclass
class CoronaLeaderboard(Leaderboard):
    colour: discord.Colour = field(default=discord.Colour.red())
    fetch_names: bool = field(default=False)
    highlight: str = field(default="Belgium")
    title: str = field(default="Corona Leaderboard")

    def get_data(self) -> list[tuple]:
        result = requests.get("https://disease.sh/v3/covid-19/countries").json()
        result.sort(key=lambda x: int(x["cases"]), reverse=True)

        data = []
        for country in result:
            data.append((country["country"], f"{country['cases']:,}", country["cases"]))

        return data

    def get_value(self, data: tuple):
        return data[2]


@dataclass
class DinksLeaderboard(Leaderboard):
    title: str = field(default="Dinks Leaderboard")

    def get_data(self) -> list[tuple]:
        entries = currency.getAllRows()
        platDinks = currency.getAllPlatDinks()

        # Take platinum dinks into account
        for i, user in enumerate(entries):
            if str(user[0]) in platDinks:
                # Tuples don't support assignment, cast to list
                user = list(user)
                user[1] += platDinks[str(user[0])] * Numbers.q.value
                entries[i] = user

        return entries

    def get_value(self, data: tuple):
        return float(data[1]) + float(data[3])

    @property
    def empty_description(self) -> str:
        return "Er zijn nog geen personen met Didier Dinks."


@dataclass
class MessageLeaderboard(Leaderboard):
    title: str = field(default="Message Leaderboard")
    message_count: int = field(init=False)

    def get_data(self) -> list[tuple]:
        entries = stats.getAllRows()
        self.message_count = stats.getTotalMessageCount()
        return entries

    def get_value(self, data: tuple):
        return round(int(data[11]))

    def format_entry_data(self, data: tuple) -> str:
        perc = round(data[2] * 100 / self.message_count, 2)
        return f"{data[2]:,} | {perc}%"


@dataclass
class MuttnLeaderboard(Leaderboard):
    title: str = field(default="Muttn Leaderboard")

    def get_data(self) -> list[tuple]:
        return muttn.getAllRows()

    def get_value(self, data: tuple):
        return round(float(data[1]), 2)

    def format_entry_data(self, data: tuple) -> str:
        return f"{data[2]}%"

    def empty_description(self) -> str:
        return "Der zittn nog geen muttns in de server."


@dataclass
class PokeLeaderboard(Leaderboard):
    title: str = field(default="Poke Leaderboard")

    def get_data(self) -> list[tuple]:
        data = stats.getAllRows()
        blacklist = poke.getAllBlacklistedUsers()
        return list(filter(lambda x: x[0] not in blacklist, data))

    def get_value(self, data: tuple):
        return round(int(data[1]))

    @property
    def empty_description(self) -> str:
        return "Er is nog niemand getikt."


@dataclass
class RobLeaderboard(Leaderboard):
    title: str = field(default="Rob Leaderboard")

    def get_data(self) -> list[tuple]:
        return list(stats.getAllRows())

    def get_value(self, data: tuple):
        return math.floor(float(data[4]))

    @property
    def empty_description(self) -> str:
        return "Er heeft nog niemand Didier Dinks gestolen."


@dataclass
class XPLeaderboard(Leaderboard):
    title: str = field(default="XP Leaderboard")

    def get_data(self) -> list[tuple]:
        return stats.getAllRows()

    def get_value(self, data: tuple):
        return round(int(data[12]))

    def format_entry_data(self, data: tuple) -> str:
        entry = data[2]
        return f"Level {xp.calculate_level(entry):,} | {entry:,} XP"
