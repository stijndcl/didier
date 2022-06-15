from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from didier import Didier


class School(commands.Cog):
    """School-related commands"""

    client: Didier

    # Context-menu references
    _pin_ctx_menu: app_commands.ContextMenu

    def __init__(self, client: Didier):
        self.client = client

        self._pin_ctx_menu = app_commands.ContextMenu(name="Pin", callback=self.pin_ctx)
        self.client.tree.add_command(self._pin_ctx_menu)

    async def cog_unload(self) -> None:
        """Remove the commands when the cog is unloaded"""
        self.client.tree.remove_command(self._pin_ctx_menu.name, type=self._pin_ctx_menu.type)

    @commands.command(name="Pin", usage="[Message]")
    async def pin(self, ctx: commands.Context, message: Optional[discord.Message] = None):
        """Pin a message in the current channel"""
        # If no message was passed, allow replying to the message that should be pinned
        if message is None and ctx.message.reference is not None:
            message = await self.client.resolve_message(ctx.message.reference)

        # Didn't fix it, sad
        if message is None:
            return await ctx.reply("Er is geen bericht om te pinnen.", delete_after=10)

        if message.is_system():
            return await ctx.reply("Dus jij wil system messages pinnen?\nMag niet.")

        await message.pin(reason=f"Didier Pin door {ctx.author.display_name}")
        await message.add_reaction("📌")

    async def pin_ctx(self, interaction: discord.Interaction, message: discord.Message):
        """Pin a message in the current channel"""
        # Is already pinned
        if message.pinned:
            return await interaction.response.send_message("Dit bericht staat al gepind.", ephemeral=True)

        if message.is_system():
            return await interaction.response.send_message(
                "Dus jij wil system messages pinnen?\nMag niet.", ephemeral=True
            )

        await message.pin(reason=f"Didier Pin door {interaction.user.display_name}")
        await message.add_reaction("📌")
        return await interaction.response.send_message("📌", ephemeral=True)


async def setup(client: Didier):
    """Load the cog"""
    await client.add_cog(School(client))
