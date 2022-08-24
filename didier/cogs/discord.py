from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from database.crud import birthdays
from didier import Didier
from didier.utils.types.datetime import str_to_date
from didier.utils.types.string import leading


class Discord(commands.Cog):
    """Cog for commands related to Discord, servers, and members"""

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

    @commands.group(name="Birthday", aliases=["Bd", "Birthdays"], case_insensitive=True, invoke_without_command=True)
    async def birthday(self, ctx: commands.Context, user: discord.User = None):
        """Command to check the birthday of a user"""
        user_id = (user and user.id) or ctx.author.id
        async with self.client.postgres_session as session:
            birthday = await birthdays.get_birthday_for_user(session, user_id)

        name = "Jouw" if user is None else f"{user.display_name}'s"

        if birthday is None:
            return await ctx.reply(f"{name} verjaardag zit niet in de database.", mention_author=False)

        day, month = leading("0", str(birthday.birthday.day)), leading("0", str(birthday.birthday.month))

        return await ctx.reply(f"{name} verjaardag staat ingesteld op **{day}/{month}**.", mention_author=False)

    @birthday.command(name="Set", aliases=["Config"])
    async def birthday_set(self, ctx: commands.Context, date_str: str):
        """Command to set your birthday"""
        try:
            default_year = 2001
            date = str_to_date(date_str, formats=["%d/%m/%Y", "%d/%m/%y", "%d/%m"])

            # If no year was passed, make it 2001 by default
            if date_str.count("/") == 1:
                date.replace(year=default_year)

        except ValueError:
            return await ctx.reply(f"`{date_str}` is geen geldige datum.", mention_author=False)

        async with self.client.postgres_session as session:
            await birthdays.add_birthday(session, ctx.author.id, date)
            await self.client.confirm_message(ctx.message)

    @commands.command(name="Join", usage="[Thread]")
    async def join(self, ctx: commands.Context, thread: discord.Thread):
        """Make Didier join a thread"""
        if thread.me is not None:
            return await ctx.reply()

    @commands.command(name="Pin", usage="[Message]")
    async def pin(self, ctx: commands.Context, message: Optional[discord.Message] = None):
        """Pin a message in the current channel"""
        # If no message was passed, allow replying to the message that should be pinned
        if message is None and ctx.message.reference is not None:
            message = await self.client.resolve_message(ctx.message.reference)

        # Didn't fix it, sad
        if message is None:
            return await ctx.reply("Found no message to pin.", delete_after=10)

        if message.pinned:
            return await ctx.reply("This message has already been pinned.", delete_after=10)

        if message.is_system():
            return await ctx.reply("Dus jij wil system messages pinnen?\nMag niet.")

        await message.pin(reason=f"Didier Pin by {ctx.author.display_name}")
        await message.add_reaction("📌")

    async def pin_ctx(self, interaction: discord.Interaction, message: discord.Message):
        """Pin a message in the current channel"""
        # Is already pinned
        if message.pinned:
            return await interaction.response.send_message("This message is already pinned.", ephemeral=True)

        if message.is_system():
            return await interaction.response.send_message(
                "Dus jij wil system messages pinnen?\nMag niet.", ephemeral=True
            )

        await message.pin(reason=f"Didier Pin by {interaction.user.display_name}")
        await message.add_reaction("📌")
        return await interaction.response.send_message("📌", ephemeral=True)


async def setup(client: Didier):
    """Load the cog"""
    await client.add_cog(Discord(client))
