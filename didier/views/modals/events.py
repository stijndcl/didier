from zoneinfo import ZoneInfo

import discord
from dateutil.parser import ParserError, parse
from overrides import overrides

from database.crud.events import add_event
from didier import Didier

__all__ = ["AddEvent"]


class AddEvent(discord.ui.Modal, title="Add Event"):
    """Modal to add a new event"""

    name: discord.ui.TextInput = discord.ui.TextInput(label="Name", style=discord.TextStyle.short, required=True)
    description: discord.ui.TextInput = discord.ui.TextInput(
        label="Description", style=discord.TextStyle.paragraph, required=False, default=None
    )
    channel: discord.ui.TextInput = discord.ui.TextInput(
        label="Channel id", style=discord.TextStyle.short, required=True, placeholder="676713433567199232"
    )
    timestamp: discord.ui.TextInput = discord.ui.TextInput(
        label="Date", style=discord.TextStyle.short, required=True, placeholder="21/02/2020 21:21:00"
    )

    client: Didier

    def __init__(self, client: Didier, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = client

    @overrides
    async def on_submit(self, interaction: discord.Interaction) -> None:
        try:
            parse(self.timestamp.value, dayfirst=True).replace(tzinfo=ZoneInfo("Europe/Brussels"))
        except ParserError:
            return await interaction.response.send_message("Unable to parse date argument.", ephemeral=True)

        if self.client.get_channel(int(self.channel.value)) is None:
            return await interaction.response.send_message(
                f"Unable to find channel `{self.channel.value}`", ephemeral=True
            )

        async with self.client.postgres_session as session:
            event = await add_event(
                session,
                name=self.name.value,
                description=self.description.value,
                date_str=self.timestamp.value,
                channel_id=int(self.channel.value),
            )

        return await interaction.response.send_message(f"Successfully added event `{event.event_id}`.", ephemeral=True)
