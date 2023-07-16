import traceback
from zoneinfo import ZoneInfo

import discord
from dateutil.parser import ParserError, parse
from overrides import overrides

from database.crud.events import add_event
from didier import Didier

__all__ = ["AddEvent"]

from didier.utils.discord.channels import NON_MESSAGEABLE_CHANNEL_TYPES


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
        await interaction.response.defer(ephemeral=True)

        try:
            parse(self.timestamp.value, dayfirst=True).replace(tzinfo=ZoneInfo("Europe/Brussels"))
        except ParserError:
            return await interaction.followup.send("Unable to parse date argument.")

        channel = self.client.get_channel(int(self.channel.value))

        if channel is None:
            return await interaction.followup.send(f"Unable to find channel with id `{self.channel.value}`")

        if isinstance(channel, NON_MESSAGEABLE_CHANNEL_TYPES):
            return await interaction.followup.send(f"Channel with id `{self.channel.value}` is not messageable.")

        async with self.client.postgres_session as session:
            event = await add_event(
                session,
                name=self.name.value,
                description=self.description.value,
                date_str=self.timestamp.value,
                channel_id=int(self.channel.value),
            )

        await interaction.followup.send(f"Successfully added event `{event.event_id}`.")
        self.client.dispatch("event_create", event)

    @overrides
    async def on_error(self, interaction: discord.Interaction, error: Exception):  # type: ignore
        await interaction.followup.send("Something went wrong.", ephemeral=True)
        traceback.print_tb(error.__traceback__)
