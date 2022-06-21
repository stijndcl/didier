import traceback

import discord


class CreateCustomCommand(discord.ui.Modal, title="Custom Command"):
    """Modal shown to visually create custom commands"""

    name = discord.ui.TextInput(label="Name", placeholder="Name of the command...")

    response = discord.ui.TextInput(
        label="Response", style=discord.TextStyle.long, placeholder="Response of the command...", max_length=2000
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Submitted", ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message("Errored", ephemeral=True)
        traceback.print_tb(error.__traceback__)
