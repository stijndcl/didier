from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Union

import discord
from discord import ApplicationContext
from discord.ext import pages
from discord.ext.commands import Context


@dataclass
class Paginated(ABC):
    """Abstract class to support paginated menus easily"""
    ctx: Union[ApplicationContext, Context]
    title: str
    data: list[tuple] = None
    per_page: int = 10
    colour: discord.Colour = discord.Colour.blue()

    def create_embed(self, description: str) -> discord.Embed:
        embed = discord.Embed(colour=self.colour)
        embed.set_author(name=self.title)
        embed.description = description

        return embed

    @abstractmethod
    def format_entry(self, index: int, value: tuple) -> str:
        pass

    def create_pages(self, data: list[tuple]) -> list[discord.Embed]:
        # Amount of entries added to this page
        added = 0
        page_list = []

        description = ""
        for i, v in enumerate(data):
            s = self.format_entry(i, v)

            description += s + "\n"
            added += 1

            # Page full, create an embed & change counters
            if added == self.per_page:
                embed = self.create_embed(description)

                description = ""
                added = 0
                page_list.append(embed)

        # Add final embed if necessary
        if added != 0:
            embed = self.create_embed(description)
            page_list.append(embed)

        return page_list

    def create_paginator(self) -> pages.Paginator:
        return pages.Paginator(pages=self.create_pages(self.data), show_disabled=False, disable_on_timeout=True, timeout=30)

    async def respond(self, **kwargs) -> discord.Message:
        paginator = self.create_paginator()
        return await paginator.respond(self.ctx.interaction, **kwargs)

    async def send(self, **kwargs) -> discord.Message:
        paginator = self.create_paginator()
        return await paginator.send(self.ctx, **kwargs)
