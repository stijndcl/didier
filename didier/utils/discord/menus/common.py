from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar, cast

import discord
from discord.ext import commands
from overrides import overrides

import settings

__all__ = ["Menu", "PageSource"]


T = TypeVar("T")


class PageSource(ABC, Generic[T]):
    """Base class that handles the embeds displayed in a menu"""

    dataset: list[T]
    embeds: list[discord.Embed] = []
    page_count: int
    per_page: int

    def __init__(self, dataset: list[T], *, per_page: int = 10):
        self.dataset = dataset
        self.per_page = per_page
        self.page_count = self._get_page_count()
        self.create_embeds()
        self._add_embed_page_footers()

    def _get_page_count(self) -> int:
        """Calculate the amount of pages required"""
        if len(self.dataset) % self.per_page == 0:
            return len(self.dataset) // self.per_page

        return (len(self.dataset) // self.per_page) + 1

    def __getitem__(self, index: int) -> discord.Embed:
        return self.embeds[index]

    def __len__(self):
        return self.page_count

    def _add_embed_page_footers(self):
        """Add the current page in the footer of every embed"""
        for i, embed in enumerate(self.embeds):
            embed.set_footer(text=f"{i + 1}/{self.page_count}")

    @abstractmethod
    def create_embeds(self):
        """Method that builds the list of embeds from the input data"""
        raise NotImplementedError


class Menu(discord.ui.View):
    """Base class for a menu"""

    ctx: commands.Context
    current_page: int = 0
    ephemeral: bool
    message: Optional[discord.Message] = None
    source: PageSource

    def __init__(self, source: PageSource, *, ephemeral: bool = False, timeout: Optional[int] = None):
        super().__init__(timeout=timeout or settings.MENU_TIMEOUT)
        self.ephemeral = ephemeral
        self.source = source

    def do_button_disabling(self):
        """Disable buttons depending on the current page"""
        first_page = cast(discord.ui.Button, self.children[0])
        first_page.disabled = self.current_page == 0

        previous_page = cast(discord.ui.Button, self.children[1])
        previous_page.disabled = self.current_page == 0

        next_page = cast(discord.ui.Button, self.children[3])
        next_page.disabled = self.current_page == len(self.source) - 1

        last_page = cast(discord.ui.Button, self.children[4])
        last_page.disabled = self.current_page == len(self.source) - 1

    async def display_current_state(self, interaction: Optional[discord.Interaction] = None):
        """Display the current state of the view

        Enable/disable buttons, show a different embed, ...
        """
        self.do_button_disabling()

        print(self.current_page, self.source[self.current_page].footer.text)

        # Send the initial message if there is none yet, else edit the existing one
        if self.message is None:
            self.message = await self.ctx.reply(
                embed=self.source[self.current_page], view=self, mention_author=False, ephemeral=self.ephemeral
            )
        elif interaction is not None:
            await interaction.response.edit_message(embed=self.source[self.current_page], view=self)

    async def start(self, ctx: commands.Context):
        """Send the initial message with this menu"""
        self.ctx = ctx
        await self.display_current_state()

    async def stop_view(self, interaction: Optional[discord.Interaction] = None):
        """Stop the view & clear all the items"""
        self.stop()
        self.clear_items()

        if interaction is not None:
            await interaction.response.edit_message(view=self)
        else:
            await self.message.edit(view=self)

    @overrides
    async def interaction_check(self, interaction: discord.Interaction, /) -> bool:
        """Only allow the person that started the menu to use the menu"""
        return interaction.user == self.ctx.author

    @overrides
    async def on_timeout(self) -> None:
        """Remove all buttons when the view times out"""
        await self.stop_view()

    @discord.ui.button(label="<<", style=discord.ButtonStyle.primary, disabled=True)
    async def first_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Button to go back to the first page"""
        self.current_page = 0
        await self.display_current_state(interaction)

    @discord.ui.button(label="<", style=discord.ButtonStyle.primary, disabled=True)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Button to go back to the previous page"""
        self.current_page -= 1
        await self.display_current_state(interaction)

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.red)
    async def stop_pages(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Button to stop the view"""
        await self.stop_view(interaction)

    @discord.ui.button(label=">", style=discord.ButtonStyle.primary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Button to show the next page"""
        self.current_page += 1
        await self.display_current_state(interaction)

    @discord.ui.button(label=">>", style=discord.ButtonStyle.primary)
    async def last_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Button to show the last page"""
        self.current_page = len(self.source) - 1
        await self.display_current_state(interaction)
