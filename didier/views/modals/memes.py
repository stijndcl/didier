import traceback

import discord.ui
from overrides import overrides

from database.schemas import MemeTemplate
from didier import Didier
from didier.data.apis.imgflip import generate_meme

__all__ = ["GenerateMeme"]


class GenerateMeme(discord.ui.Modal, title="Generate Meme"):
    """Modal to generate a meme"""

    client: Didier
    meme: MemeTemplate

    def __init__(self, client: Didier, meme: MemeTemplate, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = client
        self.meme = meme

        for i in range(meme.field_count):
            self.add_item(
                discord.ui.TextInput(
                    label=f"Field #{i + 1}",
                    placeholder="Here be funny text",
                    style=discord.TextStyle.long,
                    required=True,
                )
            )

    @overrides
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()

        fields = [item.value for item in self.children if isinstance(item, discord.ui.TextInput)]

        meme_url = await generate_meme(self.client.http_session, self.meme, fields)
        await interaction.followup.send(meme_url)

    @overrides
    async def on_error(self, interaction: discord.Interaction, error: Exception):  # type: ignore
        traceback.print_tb(error.__traceback__)
        await interaction.followup.send("Something went wrong.", ephemeral=True)
