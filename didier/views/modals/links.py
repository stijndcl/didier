import traceback

import discord.ui
from overrides import overrides

from database.crud.links import add_link
from didier import Didier

__all__ = ["AddLink"]


class AddLink(discord.ui.Modal, title="Add Link"):
    """Modal to add a new link"""

    name: discord.ui.TextInput = discord.ui.TextInput(label="Name", style=discord.TextStyle.short, placeholder="Source")
    url: discord.ui.TextInput = discord.ui.TextInput(
        label="URL", style=discord.TextStyle.short, placeholder="https://github.com/stijndcl/didier"
    )

    client: Didier

    def __init__(self, client: Didier, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = client

    @overrides
    async def on_submit(self, interaction: discord.Interaction):
        if self.name.value is None:
            return await interaction.response.send_message("Required field `Name` cannot be empty.", ephemeral=True)

        if self.url.value is None:
            return await interaction.response.send_message("Required field `URL` cannot be empty.", ephemeral=True)

        async with self.client.postgres_session as session:
            await add_link(session, self.name.value, self.url.value)
            await self.client.database_caches.links.invalidate(session)

        await interaction.response.send_message(f"Successfully added `{self.name.value.capitalize()}`.", ephemeral=True)

    @overrides
    async def on_error(self, interaction: discord.Interaction, error: Exception):  # type: ignore
        await interaction.response.send_message("Something went wrong.", ephemeral=True)
        traceback.print_tb(error.__traceback__)
