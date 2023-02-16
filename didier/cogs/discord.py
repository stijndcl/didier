from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from database.crud import birthdays, bookmarks, events, github
from database.exceptions import (
    DuplicateInsertException,
    Forbidden,
    ForbiddenNameException,
    NoResultFoundException,
)
from database.schemas import Event
from didier import Didier
from didier.exceptions import expect
from didier.menus.bookmarks import BookmarkSource
from didier.utils.discord import colours
from didier.utils.discord.assets import get_author_avatar, get_user_avatar
from didier.utils.discord.constants import Limits
from didier.utils.timer import Timer
from didier.utils.types.datetime import str_to_date, tz_aware_now
from didier.utils.types.string import abbreviate, leading
from didier.views.modals import CreateBookmark


class Discord(commands.Cog):
    """Commands related to Discord itself, which work with resources like servers and members."""

    client: Didier
    timer: Timer

    # Context-menu references
    _bookmark_ctx_menu: app_commands.ContextMenu
    _pin_ctx_menu: app_commands.ContextMenu

    def __init__(self, client: Didier):
        self.client = client

        self._bookmark_ctx_menu = app_commands.ContextMenu(name="Bookmark", callback=self._bookmark_ctx)
        self._pin_ctx_menu = app_commands.ContextMenu(name="Pin", callback=self._pin_ctx)
        self.client.tree.add_command(self._bookmark_ctx_menu)
        self.client.tree.add_command(self._pin_ctx_menu)
        self.timer = Timer(self.client)

    async def cog_unload(self) -> None:
        """Remove the commands when the cog is unloaded"""
        self.client.tree.remove_command(self._bookmark_ctx_menu.name, type=self._bookmark_ctx_menu.type)
        self.client.tree.remove_command(self._pin_ctx_menu.name, type=self._pin_ctx_menu.type)

    @commands.Cog.listener()
    async def on_event_create(self, event: Event):
        """Custom listener called when an event is created"""
        self.timer.maybe_replace_task(event)

    @commands.Cog.listener()
    async def on_timer_end(self, event_id: int):
        """Custom listener called when an event timer ends"""
        async with self.client.postgres_session as session:
            event = await events.get_event_by_id(session, event_id)

            if event is None:
                return await self.client.log_error(f"Unable to find event with id {event_id}", log_to_discord=True)

            channel = self.client.get_channel(event.notification_channel)
            human_readable_time = event.timestamp.strftime("%A, %B %d %Y - %H:%M")

            embed = discord.Embed(title=event.name, colour=discord.Colour.blue())
            embed.set_author(name="Upcoming Event")
            embed.description = event.description
            embed.add_field(
                name="Time", value=f"{human_readable_time} (<t:{round(event.timestamp.timestamp())}:R>)", inline=False
            )

            await channel.send(embed=embed)

            # Remove the database entry
            await events.delete_event_by_id(session, event.event_id)

        # Set the next timer
        self.client.loop.create_task(self.timer.update())

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
    async def birthday_set(self, ctx: commands.Context, day: str, user: Optional[discord.User] = None):
        """Set your birthday to `day`.

        Parsing of the `day`-argument happens in the following order: `DD/MM/YYYY`, `DD/MM/YY`, `DD/MM`.
        Other formats will not be accepted.
        """
        # Let owners set other people's birthdays
        if user is not None and not await self.client.is_owner(ctx.author):
            return await ctx.reply("You don't have permission to set other people's birthdays.", mention_author=False)

        # For regular users: default to your own birthday
        if user is None:
            user = ctx.author

        try:
            default_year = 2001
            date = str_to_date(day, formats=["%d/%m/%Y", "%d/%m/%y", "%d/%m"])

            # If no year was passed, make it 2001 by default
            if day.count("/") == 1:
                date.replace(year=default_year)

        except ValueError:
            return await ctx.reply(f"`{day}` is not a valid date.", mention_author=False)

        async with self.client.postgres_session as session:
            await birthdays.add_birthday(session, user.id, date)
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

        await BookmarkSource(ctx, results).start()

    async def _bookmark_ctx(self, interaction: discord.Interaction, message: discord.Message):
        """Create a bookmark out of this message"""
        modal = CreateBookmark(self.client, message.jump_url)
        await interaction.response.send_modal(modal)

    @commands.hybrid_command(name="events")
    @app_commands.rename(event_id="id")
    @app_commands.describe(event_id="The id of the event to fetch. If not passed, all events are fetched instead.")
    async def events(self, ctx: commands.Context, event_id: Optional[int] = None):
        """Show information about the event with id `event_id`.

        If no value for `event_id` is supplied, this shows all upcoming events instead.
        """
        async with ctx.typing():
            async with self.client.postgres_session as session:
                if event_id is None:
                    upcoming = await events.get_events(session, now=tz_aware_now())

                    embed = discord.Embed(title="Upcoming Events", colour=discord.Colour.blue())
                    if not upcoming:
                        embed.colour = discord.Colour.red()
                        embed.description = "There are currently no upcoming events scheduled."
                        return await ctx.reply(embed=embed, mention_author=False)

                    upcoming.sort(key=lambda e: e.timestamp.timestamp())
                    description_items = []

                    for event in upcoming:
                        description_items.append(
                            f"`{event.event_id}`: {event.name} ({discord.utils.format_dt(event.timestamp, style='R')})"
                        )

                    embed.description = "\n".join(description_items)
                    return await ctx.reply(embed=embed, mention_author=False)
                else:
                    result_event = await events.get_event_by_id(session, event_id)
                    if result_event is None:
                        return await ctx.reply(f"Found no event with id `{event_id}`.", mention_author=False)

                    embed = discord.Embed(title="Upcoming Events", colour=discord.Colour.blue())
                    embed.add_field(name="Name", value=result_event.name, inline=True)
                    embed.add_field(name="Id", value=result_event.event_id, inline=True)
                    embed.add_field(
                        name="Timer", value=discord.utils.format_dt(result_event.timestamp, style="R"), inline=True
                    )
                    embed.add_field(
                        name="Channel",
                        value=self.client.get_channel(result_event.notification_channel).mention,
                        inline=False,
                    )
                    embed.description = result_event.description
                    return await ctx.reply(embed=embed, mention_author=False)

    @commands.group(name="github", aliases=["gh", "git"], case_insensitive=True, invoke_without_command=True)
    async def github_group(self, ctx: commands.Context, user: Optional[discord.User] = None):
        """Show a user's GitHub links.

        If no user is provided, this shows your links instead.
        """
        # Default to author
        user = user or ctx.author

        embed = discord.Embed(colour=colours.github_white(), title="GitHub Links")
        embed.set_author(name=user.display_name, icon_url=get_user_avatar(user))

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

    @commands.hybrid_command(name="snipe")
    async def snipe(self, ctx: commands.Context):
        """Publicly shame people when they edit or delete one of their messages.

        Note that uncached messages will not be sniped.
        """
        if ctx.guild is None:
            return await ctx.reply("Snipe only works in servers.", mention_author=False, ephemeral=True)

        sniped_data = self.client.sniped.get(ctx.channel.id, None)
        if sniped_data is None:
            return await ctx.reply(
                "There's no one to make fun of in this channel.", mention_author=False, ephemeral=True
            )

        embed = discord.Embed(colour=discord.Colour.blue())

        embed.set_author(name=sniped_data[0].author.display_name, icon_url=get_user_avatar(sniped_data[0].author))

        if sniped_data[1] is not None:
            embed.title = "Edit Snipe"
            embed.add_field(
                name="Before", value=abbreviate(sniped_data[0].content, Limits.EMBED_FIELD_VALUE_LENGTH), inline=False
            )
            embed.add_field(
                name="After", value=abbreviate(sniped_data[1].content, Limits.EMBED_FIELD_VALUE_LENGTH), inline=False
            )
        else:
            embed.title = "Delete Snipe"
            embed.add_field(name="Message", value=sniped_data[0].content)

        return await ctx.reply(embed=embed, mention_author=False)


async def setup(client: Didier):
    """Load the cog"""
    await client.add_cog(Discord(client))
