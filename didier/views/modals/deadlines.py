import traceback

import discord.ui
from discord import Interaction
from overrides import overrides

from database.crud.deadlines import add_deadline
from database.schemas import UforaCourse

__all__ = ["AddDeadline"]

from didier import Didier


class AddDeadline(discord.ui.Modal, title="Add Deadline"):
    """Modal to add a new deadline"""

    client: Didier
    ufora_course: UforaCourse

    name: discord.ui.TextInput = discord.ui.TextInput(
        label="Name", placeholder="Project 9001", required=True, style=discord.TextStyle.short
    )
    deadline: discord.ui.TextInput = discord.ui.TextInput(
        label="Deadline", placeholder="DD/MM/YYYY HH:MM:SS*", required=True, style=discord.TextStyle.short
    )

    def __init__(self, client: Didier, ufora_course: UforaCourse, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = client
        self.ufora_course = ufora_course

    @overrides
    async def on_submit(self, interaction: Interaction):
        if not self.name.value or not self.deadline.value:
            return await interaction.response.send_message("Required fields cannot be empty.", ephemeral=True)

        async with self.client.postgres_session as session:
            await add_deadline(session, self.ufora_course.course_id, self.name.value, self.deadline.value)

        await interaction.response.send_message("Successfully added new deadline.", ephemeral=True)

    @overrides
    async def on_error(self, interaction: Interaction, error: Exception):  # type: ignore
        await interaction.response.send_message("Something went wrong.", ephemeral=True)
        traceback.print_tb(error.__traceback__)
