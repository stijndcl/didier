import traceback

import discord
from overrides import overrides

from database.crud.dad_jokes import add_dad_joke
from didier import Didier

__all__ = ["AddDadJoke"]


class AddDadJoke(discord.ui.Modal, title="Add Dad Joke"):
    """Modal to add a new dad joke"""

    joke: discord.ui.TextInput = discord.ui.TextInput(
        label="Joke",
        placeholder="I sold our vacuum cleaner, it was just gathering dust.",
        style=discord.TextStyle.long,
    )

    client: Didier

    def __init__(self, client: Didier, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = client

    @overrides
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        async with self.client.postgres_session as session:
            joke = await add_dad_joke(session, str(self.joke.value))

        await interaction.followup.send(f"Successfully added joke #{joke.dad_joke_id}")

    @overrides
    async def on_error(self, interaction: discord.Interaction, error: Exception):  # type: ignore
        await interaction.followup.send("Something went wrong.", ephemeral=True)
        traceback.print_tb(error.__traceback__)
