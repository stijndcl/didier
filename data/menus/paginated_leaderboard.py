from typing import Callable

import discord
from discord import ApplicationContext
from discord.ext import menus, pages
from dataclasses import dataclass

from discord.ext.commands import Context

from functions.utils import get_display_name


@dataclass
class Leaderboard:
    ctx: Context
    title: str
    data: list
    highlight: str = None
    format_f: Callable = None
    per_page: int = 10
    colour: discord.Colour = discord.Colour.blue()
    fetch_names: bool = False

    def __post_init__(self):
        if self.format_f is None:
            self .format_f = lambda x: x

    def _should_highlight(self, data) -> bool:
        """Check if an entry should be highlighted"""
        if self.fetch_names:
            return data == self.ctx.author.id

        return data == self.highlight

    def _format(self, index: int, data: tuple) -> str:
        name = data[0]

        if self.fetch_names:
            name = get_display_name(self.ctx, int(data[0]))

        s = f"{index + 1}: {name} ({self.format_f(data[1])})"

        return s

    def _get_page_count(self) -> int:
        """Get the amount of pages required to represent this data"""
        count = len(self.data) // self.per_page
        if len(self.data) % self.per_page != 0:
            count += 1

        return count

    def _create_embed(self, description: str) -> discord.Embed:
        embed = discord.Embed(colour=self.colour)
        embed.set_author(name=self.title)
        embed.description = description

        return embed

    def create_pages(self) -> list[discord.Embed]:
        # Amount of entries added to this page
        added = 0
        page_list = []

        description = ""
        for i, v in enumerate(self.data):
            s = self._format(i, v)

            if self._should_highlight(v[0]):
                s = f"**{s}**"

            description += s + "\n"
            added += 1

            # Page full, create an embed & change counters
            if added == self.per_page:
                embed = self._create_embed(description)

                description = ""
                added = 0
                page_list.append(embed)

        # Add final embed
        if added != 0:
            embed = self._create_embed(description)
            page_list.append(embed)

        return page_list

    def create_paginator(self) -> pages.Paginator:
        return pages.Paginator(pages=self.create_pages(), show_disabled=False, disable_on_timeout=True, timeout=30)

    async def respond(self, ctx: ApplicationContext, **kwargs) -> discord.Message:
        paginator = self.create_paginator()
        return await paginator.respond(ctx.interaction, **kwargs)

    async def send(self, ctx: Context, **kwargs) -> discord.Message:
        paginator = self.create_paginator()
        return await paginator.send(ctx, **kwargs)


class Source(menus.ListPageSource):
    def __init__(self, data, name, colour=discord.Colour.blue()):
        super().__init__(data, per_page=10)
        self.name = name
        self.colour = colour

    async def format_page(self, menu: menus.MenuPages, entries):
        offset = menu.current_page * self.per_page

        description = ""
        for i, v in enumerate(entries, start=offset):
            # Check if the person's name has to be highlighted
            if v.startswith("**") and v.endswith("**"):
                description += "**"
                v = v[2:]
            description += "{}: {}\n".format(i + 1, v)
        embed = discord.Embed(colour=self.colour)
        embed.set_author(name=self.name)
        embed.description = description
        embed.set_footer(text="{}/{}".format(menu.current_page + 1, self.get_max_pages()))
        return embed


class Pages(menus.MenuPages):
    def __init__(self, source, clear_reactions_after, timeout=30.0):
        super().__init__(source, timeout=timeout, delete_message_after=True, clear_reactions_after=clear_reactions_after)
