from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from database.crud import birthdays, bookmarks
from database.exceptions import DuplicateInsertException, ForbiddenNameException
from didier import Didier
from didier.exceptions import expect
from didier.utils.types.datetime import str_to_date
from didier.utils.types.string import leading
from didier.views.modals import CreateBookmark


class Discord(commands.Cog):
    """Cog for commands related to Discord, servers, and members"""

    client: Didier

    # Context-menu references
    _bookmark_ctx_menu: app_commands.ContextMenu
    _pin_ctx_menu: app_commands.ContextMenu

    def __init__(self, client: Didier):
        self.client = client

        self._bookmark_ctx_menu = app_commands.ContextMenu(name="Bookmark", callback=self._bookmark_ctx)
        self._pin_ctx_menu = app_commands.ContextMenu(name="Pin", callback=self._pin_ctx)
        self.client.tree.add_command(self._bookmark_ctx_menu)
        self.client.tree.add_command(self._pin_ctx_menu)

    async def cog_unload(self) -> None:
        """Remove the commands when the cog is unloaded"""
        self.client.tree.remove_command(self._bookmark_ctx_menu.name, type=self._bookmark_ctx_menu.type)
        self.client.tree.remove_command(self._pin_ctx_menu.name, type=self._pin_ctx_menu.type)

    @commands.group(name="Birthday", aliases=["Bd", "Birthdays"], case_insensitive=True, invoke_without_command=True)
    async def birthday(self, ctx: commands.Context, user: discord.User = None):
        """Command to check the birthday of a user"""
        user_id = (user and user.id) or ctx.author.id
        async with self.client.postgres_session as session:
            birthday = await birthdays.get_birthday_for_user(session, user_id)

        name = "Your" if user is None else f"{user.display_name}'s"

        if birthday is None:
            return await ctx.reply(f"I don't know {name} birthday.", mention_author=False)

        day, month = leading("0", str(birthday.birthday.day)), leading("0", str(birthday.birthday.month))

        return await ctx.reply(f"{name} birthday is set to **{day}/{month}**.", mention_author=False)

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
            return await ctx.reply(f"`{date_str}` is not a valid date.", mention_author=False)

        async with self.client.postgres_session as session:
            await birthdays.add_birthday(session, ctx.author.id, date)
            await self.client.confirm_message(ctx.message)

    @commands.group(name="Bookmark", aliases=["Bm", "Bookmarks"], case_insensitive=True, invoke_without_command=True)
    async def bookmark(self, ctx: commands.Context, label: str):
        """Post a bookmarked message"""
        async with self.client.postgres_session as session:
            result = expect(
                await bookmarks.get_bookmark_by_name(session, ctx.author.id, label),
                entity_type="bookmark",
                argument="label",
            )
            await ctx.reply(result.jump_url, mention_author=False)

    @bookmark.command(name="Create", aliases=["New"])
    async def bookmark_create(self, ctx: commands.Context, label: str, message: Optional[discord.Message]):
        """Create a new bookmark"""
        # If no message was passed, allow replying to the message that should be bookmarked
        if message is None and ctx.message.reference is not None:
            message = await self.client.resolve_message(ctx.message.reference)

        # Didn't fix it, so no message was found
        if message is None:
            return await ctx.reply("Found no message to bookmark.", delete_after=10)

        # Create new bookmark

        try:
            async with self.client.postgres_session as session:
                bm = await bookmarks.create_bookmark(session, ctx.author.id, label, message.jump_url)
                await ctx.reply(f"Bookmark `{label}` successfully created (`#{bm.bookmark_id}`).", mention_author=False)
        except DuplicateInsertException:
            # Label is already in use
            return await ctx.reply(f"You already have a bookmark named `{label}`.", mention_author=False)
        except ForbiddenNameException:
            # Label isn't allowed
            return await ctx.reply(f"Bookmarks cannot be named `{label}`.", mention_author=False)

    @bookmark.command(name="Search", aliases=["List", "Ls"])
    async def bookmark_search(self, ctx: commands.Context, *, query: Optional[str] = None):
        """Search through the list of bookmarks"""

    async def _bookmark_ctx(self, interaction: discord.Interaction, message: discord.Message):
        """Create a bookmark out of this message"""
        modal = CreateBookmark(self.client, message.jump_url)
        await interaction.response.send_modal(modal)

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

    async def _pin_ctx(self, interaction: discord.Interaction, message: discord.Message):
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
