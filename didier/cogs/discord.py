from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from database.crud import birthdays, bookmarks, github
from database.exceptions import (
    DuplicateInsertException,
    Forbidden,
    ForbiddenNameException,
    NoResultFoundException,
)
from didier import Didier
from didier.exceptions import expect
from didier.menus.bookmarks import BookmarkSource
from didier.menus.common import Menu
from didier.utils.discord import colours
from didier.utils.discord.assets import get_author_avatar
from didier.utils.types.datetime import str_to_date
from didier.utils.types.string import leading
from didier.views.modals import CreateBookmark


class Discord(commands.Cog):
    """Commands related to Discord itself, which work with resources like servers and members."""

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

    @commands.group(name="birthday", aliases=["bd", "birthdays"], case_insensitive=True, invoke_without_command=True)
    async def birthday(self, ctx: commands.Context, user: discord.User = None):
        """Command to check the birthday of `user`.

        Not passing an argument for `user` will show yours instead.
        """
        user_id = (user and user.id) or ctx.author.id
        async with self.client.postgres_session as session:
            birthday = await birthdays.get_birthday_for_user(session, user_id)

        name: Optional[str] = f"{user.display_name}'s" if user is not None else None

        if birthday is None:
            return await ctx.reply(f"I don't know {name or 'your'} birthday.", mention_author=False)

        day, month = leading("0", str(birthday.birthday.day)), leading("0", str(birthday.birthday.month))
        return await ctx.reply(f"{name or 'Your'} birthday is set to **{day}/{month}**.", mention_author=False)

    @birthday.command(name="set", aliases=["config"])
    async def birthday_set(self, ctx: commands.Context, day: str):
        """Set your birthday to `day`.

        Parsing of the `day`-argument happens in the following order: `DD/MM/YYYY`, `DD/MM/YY`, `DD/MM`.
        Other formats will not be accepted.
        """
        try:
            default_year = 2001
            date = str_to_date(day, formats=["%d/%m/%Y", "%d/%m/%y", "%d/%m"])

            # If no year was passed, make it 2001 by default
            if day.count("/") == 1:
                date.replace(year=default_year)

        except ValueError:
            return await ctx.reply(f"`{day}` is not a valid date.", mention_author=False)

        async with self.client.postgres_session as session:
            await birthdays.add_birthday(session, ctx.author.id, date)
            await self.client.confirm_message(ctx.message)

    @commands.group(name="bookmark", aliases=["bm", "bookmarks"], case_insensitive=True, invoke_without_command=True)
    async def bookmark(self, ctx: commands.Context, *, label: Optional[str] = None):
        """Post the message bookmarked with `label`.

        The `label`-argument can contain spaces and does not require quotes around it. For example:
        ```
        didier bookmark some label with multiple words
        ```

        When no value for `label` is provided, this is a shortcut to `bookmark search`.
        """
        # No label: shortcut to display bookmarks
        if label is None:
            return await self.bookmark_search(ctx, query=None)

        async with self.client.postgres_session as session:
            result = expect(
                await bookmarks.get_bookmark_by_name(session, ctx.author.id, label),
                entity_type="bookmark",
                argument="label",
            )
            await ctx.reply(result.jump_url, mention_author=False)

    @bookmark.command(name="create", aliases=["new"])
    async def bookmark_create(self, ctx: commands.Context, label: str, message: Optional[discord.Message]):
        """Create a new bookmark for message `message` with label `label`.

        Instead of the link to a message, you can also reply to the message you wish to bookmark. In this case,
        the `message`-argument can be left out.

        `label` can not be names (or aliases) of subcommands. However, names with spaces are allowed. If you wish
        to use a name with spaces, it must be wrapped in "quotes".
        """
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

    @bookmark.command(name="delete", aliases=["rm"])
    async def bookmark_delete(self, ctx: commands.Context, bookmark_id: str):
        """Delete the bookmark with id `bookmark_id`.

        You can only delete your own bookmarks.
        """
        # The bookmarks are displayed with a hashtag in front of the id
        # so strip it out in case people want to try and use this
        bookmark_id = bookmark_id.removeprefix("#")

        try:
            bookmark_id_int = int(bookmark_id)
        except ValueError:
            return await ctx.reply(f"`{bookmark_id}` is not a valid bookmark id.", mention_author=False)

        async with self.client.postgres_session as session:
            try:
                await bookmarks.delete_bookmark_by_id(session, ctx.author.id, bookmark_id_int)
            except NoResultFoundException:
                return await ctx.reply(f"Found no bookmark with id `#{bookmark_id_int}`.", mention_author=False)
            except Forbidden:
                return await ctx.reply(f"You don't own bookmark `#{bookmark_id_int}`.", mention_author=False)

        return await ctx.reply(f"Successfully deleted bookmark `#{bookmark_id_int}`.", mention_author=False)

    @bookmark.command(name="search", aliases=["list", "ls"])
    async def bookmark_search(self, ctx: commands.Context, *, query: Optional[str] = None):
        """Search through the list of bookmarks.

        If a value for `query` was provided, results will be filtered down to only labels that include `query`.
        Otherwise, all bookmarks are displayed.

        The `query`-argument can contain spaces and does not require quotes around it. For example:
        ```
        didier bookmark search some query with multiple words
        ```
        """
        async with self.client.postgres_session as session:
            results = await bookmarks.get_bookmarks(session, ctx.author.id, query=query)

        if not results:
            embed = discord.Embed(title="Bookmarks", colour=discord.Colour.red())
            avatar_url = get_author_avatar(ctx).url
            embed.set_author(name=ctx.author.display_name, icon_url=avatar_url)
            embed.description = "You haven't created any bookmarks yet."
            return await ctx.reply(embed=embed, mention_author=False)

        source = BookmarkSource(ctx, results)
        menu = Menu(source)
        await menu.start(ctx)

    async def _bookmark_ctx(self, interaction: discord.Interaction, message: discord.Message):
        """Create a bookmark out of this message"""
        modal = CreateBookmark(self.client, message.jump_url)
        await interaction.response.send_modal(modal)

    @commands.group(name="github", aliases=["gh", "git"], case_insensitive=True, invoke_without_command=True)
    async def github_group(self, ctx: commands.Context, user: Optional[discord.User] = None):
        """Show a user's GitHub links.

        If no user is provided, this shows your links instead.
        """
        # Default to author
        user = user or ctx.author

        embed = discord.Embed(colour=colours.github_white(), title="GitHub Links")
        embed.set_author(
            name=user.display_name, icon_url=user.avatar.url if user.avatar is not None else user.default_avatar.url
        )

        embed.set_footer(text="Links can be added using didier github add <link>.")

        async with self.client.postgres_session as session:
            links = await github.get_github_links(session, user.id)

        if not links:
            embed.description = "This user has not set any GitHub links yet."
        else:
            regular_links = []
            ugent_links = []

            for link in links:
                if "github.ugent.be" in link.url.lower():
                    ugent_links.append(f"`#{link.github_link_id}`: {link.url}")
                else:
                    regular_links.append(f"`#{link.github_link_id}`: {link.url}")

            regular_links.sort()
            ugent_links.sort()

            if ugent_links:
                embed.add_field(name="Ghent University", value="\n".join(ugent_links), inline=False)

            if regular_links:
                embed.add_field(name="Other", value="\n".join(regular_links), inline=False)

        return await ctx.reply(embed=embed, mention_author=False)

    @github_group.command(name="add", aliases=["create", "insert"])
    async def github_add(self, ctx: commands.Context, link: str):
        """Add a new link into the database."""
        # Remove wrapping <brackets> which can be used to escape Discord embeds
        link = link.removeprefix("<").removesuffix(">")

        async with self.client.postgres_session as session:
            try:
                gh_link = await github.add_github_link(session, ctx.author.id, link)
            except DuplicateInsertException:
                return await ctx.reply("This link has already been registered by someone.", mention_author=False)

        await self.client.confirm_message(ctx.message)
        return await ctx.reply(f"Successfully inserted link `#{gh_link.github_link_id}`.", mention_author=False)

    @github_group.command(name="delete", aliases=["del", "remove", "rm"])
    async def github_delete(self, ctx: commands.Context, link_id: str):
        """Delete the link with it `link_id` from the database.

        You can only delete your own links.
        """
        try:
            link_id_int = int(link_id.removeprefix("#"))
        except ValueError:
            return await ctx.reply(f"`{link_id}` is not a valid link id.", mention_author=False)

        async with self.client.postgres_session as session:
            try:
                await github.delete_github_link_by_id(session, ctx.author.id, link_id_int)
            except NoResultFoundException:
                return await ctx.reply(f"Found no GitHub link with id `#{link_id_int}`.", mention_author=False)
            except Forbidden:
                return await ctx.reply(f"You don't own GitHub link `#{link_id_int}`.", mention_author=False)

        return await ctx.reply(f"Successfully deleted GitHub link `#{link_id_int}`.", mention_author=False)

    @commands.command(name="join")
    async def join(self, ctx: commands.Context, thread: discord.Thread):
        """Make Didier join `thread`.

        This command should generally not be necessary, as Didier automatically joins threads. However, it's possible
        that Didier is offline at the moment of a thread being created.

        Alternatively, you can also `@mention` Didier to pull him into the thread instead.
        """
        if thread.me is not None:
            return await ctx.reply()

    @commands.command(name="pin")
    async def pin(self, ctx: commands.Context, message: Optional[discord.Message] = None):
        """Pin `message` in the current channel.

        Instead of the link to a message, you can also reply to the message you wish to pin. In this case,
        the `message`-argument can be left out.
        """
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
