import traceback

import discord.ui
from overrides import overrides

from database.crud.bookmarks import create_bookmark
from database.exceptions import DuplicateInsertException, ForbiddenNameException
from didier import Didier

__all__ = ["CreateBookmark"]


class CreateBookmark(discord.ui.Modal, title="Create Bookmark"):
    """Modal to create a bookmark"""

    client: Didier
    jump_url: str

    name: discord.ui.TextInput = discord.ui.TextInput(label="Name", style=discord.TextStyle.short, required=True)

    def __init__(self, client: Didier, jump_url: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = client
        self.jump_url = jump_url

    @overrides
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        label = self.name.value.strip()

        try:
            async with self.client.postgres_session as session:
                bm = await create_bookmark(session, interaction.user.id, label, self.jump_url)
                return await interaction.followup.send(
                    f"Bookmark `{label}` successfully created (`#{bm.bookmark_id}`)."
                )
        except DuplicateInsertException:
            # Label is already in use
            return await interaction.followup.send(f"You already have a bookmark named `{label}`.")
        except ForbiddenNameException:
            # Label isn't allowed
            return await interaction.followup.send(f"Bookmarks cannot be named `{label}`.")

    @overrides
    async def on_error(self, interaction: discord.Interaction, error: Exception):  # type: ignore
        await interaction.followup.send("Something went wrong.", ephemeral=True)
        traceback.print_tb(error.__traceback__)
