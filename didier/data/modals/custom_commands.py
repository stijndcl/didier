import traceback
import typing

import discord
from overrides import overrides

from database.crud.custom_commands import create_command, edit_command
from didier import Didier

__all__ = ["CreateCustomCommand", "EditCustomCommand"]


class CreateCustomCommand(discord.ui.Modal, title="Create Custom Command"):
    """Modal to create new custom commands"""

    name: discord.ui.TextInput = discord.ui.TextInput(label="Name", placeholder="Didier")

    response: discord.ui.TextInput = discord.ui.TextInput(
        label="Response", style=discord.TextStyle.long, placeholder="Hmm?", max_length=2000
    )

    client: Didier

    def __init__(self, client: Didier, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = client

    @overrides
    async def on_submit(self, interaction: discord.Interaction):
        async with self.client.db_session as session:
            command = await create_command(session, str(self.name.value), str(self.response.value))

        await interaction.response.send_message(f"Successfully created ``{command.name}``.", ephemeral=True)

    @overrides
    async def on_error(self, interaction: discord.Interaction, error: Exception):  # type: ignore
        await interaction.response.send_message("Something went wrong.", ephemeral=True)
        traceback.print_tb(error.__traceback__)


class EditCustomCommand(discord.ui.Modal, title="Edit Custom Command"):
    """Modal to edit an existing custom command

    Fills in the current values as defaults for QOL
    """

    name: discord.ui.TextInput
    response: discord.ui.TextInput

    original_name: str

    client: Didier

    def __init__(self, client: Didier, name: str, response: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_name = name
        self.client = client

        self.add_item(discord.ui.TextInput(label="Name", placeholder="Didier", default=name))
        self.add_item(
            discord.ui.TextInput(
                label="Response", placeholder="Hmm?", default=response, style=discord.TextStyle.long, max_length=2000
            )
        )

    @overrides
    async def on_submit(self, interaction: discord.Interaction):
        name_field = typing.cast(discord.ui.TextInput, self.children[0])
        response_field = typing.cast(discord.ui.TextInput, self.children[1])

        async with self.client.db_session as session:
            await edit_command(session, self.original_name, name_field.value, response_field.value)

        await interaction.response.send_message(f"Successfully edited ``{self.original_name}``.", ephemeral=True)

    @overrides
    async def on_error(self, interaction: discord.Interaction, error: Exception):  # type: ignore
        await interaction.response.send_message("Something went wrong.", ephemeral=True)
        traceback.print_tb(error.__traceback__)
