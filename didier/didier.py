import logging
import os
import pathlib
import re
from functools import cached_property
from typing import Optional, Union

import discord
from aiohttp import ClientSession
from discord.ext import commands
from sqlalchemy.ext.asyncio import AsyncSession

import settings
from database.crud import command_stats, custom_commands
from database.engine import DBSession
from database.utils.caches import CacheManager
from didier.data.embeds.error_embed import create_error_embed
from didier.data.embeds.logging_embed import create_logging_embed
from didier.data.embeds.schedules import Schedule, parse_schedule
from didier.exceptions import GetNoneException, HTTPException, NoMatch
from didier.utils.discord.prefix import get_prefix
from didier.utils.discord.snipe import should_snipe
from didier.utils.easter_eggs import detect_easter_egg
from didier.utils.types.datetime import tz_aware_now

__all__ = ["Didier"]


logger = logging.getLogger(__name__)


class Didier(commands.Bot):
    """DIDIER <3"""

    database_caches: CacheManager
    error_channel: Optional[discord.abc.Messageable] = None
    initial_extensions: tuple[str, ...] = ()
    http_session: ClientSession
    schedules: dict[settings.ScheduleType, Schedule] = {}
    sniped: dict[int, tuple[discord.Message, Optional[discord.Message]]] = {}

    def __init__(self):
        activity = discord.Activity(type=discord.ActivityType.playing, name=settings.DISCORD_STATUS_MESSAGE)
        status = discord.Status.online

        intents = discord.Intents(
            guilds=True,
            members=True,
            message_content=True,
            emojis=True,
            messages=True,
            reactions=True,
        )

        super().__init__(
            command_prefix=get_prefix, case_insensitive=True, intents=intents, activity=activity, status=status
        )

        # I'm not creating a custom tree, this is the way to do it
        self.tree.on_error = self.on_app_command_error  # type: ignore[method-assign]

    @cached_property
    def main_guild(self) -> discord.Guild:
        """Obtain a reference to the main guild"""
        guild = self.get_guild(settings.DISCORD_MAIN_GUILD)
        if guild is None:
            raise GetNoneException("Main guild could not be found in the bot's cache")

        return guild

    @property
    def postgres_session(self) -> AsyncSession:
        """Obtain a session for the PostgreSQL database"""
        return DBSession()

    async def setup_hook(self) -> None:
        """Do some initial setup

        This hook is called once the bot is initialised
        """
        # Create directories that are ignored on GitHub
        self._create_ignored_directories()

        # Initialize caches
        self.database_caches = CacheManager()
        async with self.postgres_session as session:
            await self.database_caches.initialize_caches(session)

        # Create aiohttp session
        self.http_session = ClientSession(
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/105.0.0.0 Safari/537.36"
            }
        )

        # Load extensions
        await self._load_initial_extensions()
        await self._load_directory_extensions("didier/cogs")

    def _create_ignored_directories(self):
        """Create directories that store ignored data"""
        ignored = ["files/schedules"]

        for directory in ignored:
            pathlib.Path(directory).mkdir(exist_ok=True, parents=True)

    async def _load_initial_extensions(self):
        """Load all extensions that should  be loaded before the others"""
        for extension in self.initial_extensions:
            await self.load_extension(f"didier.{extension}")

    async def _load_directory_extensions(self, path: str):
        """Load all extensions in a given directory"""
        load_path = path.removeprefix("./").replace("/", ".")
        parent_path = load_path.removeprefix("didier.")

        # Check every file in the directory
        for file in os.listdir(path):
            # Construct a path that includes all parent packages in order to
            # Allow checking against initial extensions more easily
            full_name = parent_path + file

            # Only take Python files, and ignore the ones starting with an underscore (like __init__ and __pycache__)
            # Also ignore the files that we have already loaded previously
            if file.endswith(".py") and not file.startswith("_") and not full_name.startswith(self.initial_extensions):
                await self.load_extension(f"{load_path}.{file[:-3]}")
            elif os.path.isdir(new_path := f"{path}/{file}"):
                await self._load_directory_extensions(new_path)

    async def load_schedules(self):
        """Parse & load all schedules into memory"""
        self.schedules = {}

        async with self.postgres_session as session:
            for schedule_data in settings.SCHEDULE_DATA:
                schedule = await parse_schedule(schedule_data.name, database_session=session)
                if schedule is None:
                    continue

                self.schedules[schedule_data.name] = schedule

    async def get_reply_target(self, ctx: commands.Context) -> discord.Message:
        """Get the target message that should be replied to

        In case the invoking message is a reply to something, reply to the
        original message instead
        """
        if ctx.message.reference is not None:
            return await self.resolve_message(ctx.message.reference) or ctx.message

        return ctx.message

    async def resolve_message(self, reference: discord.MessageReference) -> Optional[discord.Message]:
        """Fetch a message from a reference"""
        # Message is in the cache, return it
        if reference.cached_message is not None:
            return reference.cached_message

        if reference.message_id is None:
            return None

        # For older messages: fetch them from the API
        channel = self.get_channel(reference.channel_id)
        if channel is None or isinstance(
            channel,
            (discord.CategoryChannel, discord.ForumChannel, discord.abc.PrivateChannel),
        ):  # Logically this can't happen, but we have to please Mypy
            return None

        return await channel.fetch_message(reference.message_id)

    async def confirm_message(self, message: discord.Message):
        """Add a checkmark to a message"""
        await message.add_reaction("✅")

    async def reject_message(self, message: discord.Message):
        """Add an X to a message"""
        await message.add_reaction("❌")

    async def _log(self, level: int, message: str, log_to_discord: bool = True):
        """Log a message to the logging file, and optionally to the configured channel"""
        methods = {
            logging.DEBUG: logger.debug,
            logging.ERROR: logger.error,
            logging.INFO: logger.info,
            logging.WARNING: logger.warning,
        }

        methods.get(level, logger.error)(message)
        if log_to_discord and self.error_channel is not None:
            embed = create_logging_embed(level, message)
            await self.error_channel.send(embed=embed)

    async def log_error(self, message: str, log_to_discord: bool = True):
        """Log an error message"""
        await self._log(logging.ERROR, message, log_to_discord)

    async def log_warning(self, message: str, log_to_discord: bool = True):
        """Log a warning message"""
        await self._log(logging.WARNING, message, log_to_discord)

    async def _try_invoke_custom_command(self, message: discord.Message) -> bool:
        """Check if the message tries to invoke a custom command

        If it does, send the reply associated with it
        Returns a boolean indicating if a message invoked a command or not
        """
        # Doesn't start with the custom command prefix
        if not message.content.startswith(settings.DISCORD_CUSTOM_COMMAND_PREFIX):
            return False

        # Remove the prefix
        content = message.content[len(settings.DISCORD_CUSTOM_COMMAND_PREFIX) :].strip()

        # Message was just "?" (or whatever the prefix was configured to)
        if not content:
            return False

        async with self.postgres_session as session:
            command = await custom_commands.get_command(session, content)

            # Command found
            if command is not None:
                await message.reply(command.response, mention_author=False)
                return True

        # Nothing found
        return False

    async def on_app_command_completion(
        self,
        interaction: discord.Interaction,
        command: Union[discord.app_commands.Command, discord.app_commands.ContextMenu],
    ):
        """Event triggered when an app command completes successfully"""
        ctx = await commands.Context.from_interaction(interaction)

        async with self.postgres_session as session:
            await command_stats.register_command_invocation(session, ctx, command, tz_aware_now())

    async def on_app_command_error(self, interaction: discord.Interaction, exception: Exception):
        """Event triggered when an application command errors"""
        # If commands have their own error handler, let it handle the error instead
        if hasattr(interaction.command, "on_error"):
            return

        # Unwrap exception
        if isinstance(exception, discord.app_commands.CommandInvokeError):
            exception = exception.original

        if isinstance(exception, (NoMatch, HTTPException)):
            if interaction.response.is_done():
                return await interaction.response.send_message(str(exception), ephemeral=True)
            else:
                return await interaction.followup.send(str(exception), ephemeral=True)

        await interaction.response.send_message("Something went wrong processing this command.", ephemeral=True)

        if self.error_channel is not None:
            embed = create_error_embed(await commands.Context.from_interaction(interaction), exception)
            await self.error_channel.send(embed=embed)

    async def on_command_completion(self, ctx: commands.Context):
        """Event triggered when a message command completes successfully"""
        # Hybrid command invocation triggers both this handler and on_app_command_completion
        # We handle it in the correct place
        if ctx.interaction is not None:
            return

        async with self.postgres_session as session:
            await command_stats.register_command_invocation(session, ctx, ctx.command, tz_aware_now())

    async def on_command_error(self, ctx: commands.Context, exception: commands.CommandError, /):
        """Event triggered when a message command errors"""
        # If working locally, print everything to your console
        if settings.SANDBOX:
            await super().on_command_error(ctx, exception)
            return

        # If commands have their own error handler, let it handle the error instead
        if hasattr(ctx.command, "on_error"):
            return

        # Hybrid command errors are wrapped in an additional error, so wrap it back out
        if isinstance(exception, commands.HybridCommandError):
            exception = exception.original  # type: ignore[assignment]

        # Ignore exceptions that aren't important
        if isinstance(
            exception,
            (
                commands.CommandNotFound,
                commands.CheckFailure,
                commands.TooManyArguments,
            ),
        ):
            return

        # Responses to things that go wrong during processing of commands
        if isinstance(
            exception,
            (discord.app_commands.CommandInvokeError, commands.CommandInvokeError),
        ) and isinstance(
            exception.original,
            (
                NoMatch,
                HTTPException,
            ),
        ):
            return await ctx.reply(str(exception.original), mention_author=False)

        if isinstance(exception, commands.MessageNotFound):
            return await ctx.reply("This message could not be found.", ephemeral=True, delete_after=10)

        if isinstance(exception, (commands.MissingRequiredArgument,)):
            message = str(exception)

            match = re.search(r"(.*) is a required argument that is missing\.", message)
            if match is not None and match.groups():
                message = f"Found no value for the `{match.groups()[0]}`-argument."

            return await ctx.reply(message, ephemeral=True, delete_after=10)

        if isinstance(
            exception,
            (
                commands.BadArgument,
                commands.UnexpectedQuoteError,
                commands.ExpectedClosingQuoteError,
            ),
        ):
            return await ctx.reply("Invalid arguments.", ephemeral=True, delete_after=10)

        # Print everything that we care about to the logs/stderr
        await super().on_command_error(ctx, exception)

        if self.error_channel is not None:
            embed = create_error_embed(ctx, exception)
            await self.error_channel.send(embed=embed)

    async def on_message(self, message: discord.Message, /) -> None:
        """Event triggered when a message is sent"""
        # Ignore messages by bots
        if message.author.bot:
            return

        # Boos react to people that say Dider
        if "dider" in message.content.lower() and self.user is not None and message.author.id != self.user.id:
            await message.add_reaction(settings.DISCORD_BOOS_REACT)

        # Potential custom command
        if await self._try_invoke_custom_command(message):
            return

        await self.process_commands(message)

        easter_egg = await detect_easter_egg(self, message, self.database_caches.easter_eggs)
        if easter_egg is not None:
            await message.reply(easter_egg, mention_author=False)

    async def on_message_delete(self, message: discord.Message):
        """Event triggered when a message is deleted"""
        if not should_snipe(message):
            return

        self.sniped[message.channel.id] = (
            message,
            None,
        )

    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        """Event triggered when a message is edited"""
        if not should_snipe(before):
            return

        # If the edited message is currently present in the snipe cache,
        # don't update the <before>, but instead change the <after>
        existing = self.sniped.get(before.channel.id)
        if existing is not None and existing[0].id == before.id:
            before = existing[0]

        self.sniped[before.channel.id] = (
            before,
            after,
        )

    async def on_ready(self):
        """Event triggered when the bot is ready"""
        print(settings.DISCORD_READY_MESSAGE)

    async def on_task_error(self, exception: Exception):
        """Event triggered when a task raises an exception"""
        if self.error_channel:
            embed = create_error_embed(None, exception)
            await self.error_channel.send(embed=embed)

    async def on_thread_create(self, thread: discord.Thread):
        """Event triggered when a new thread is created"""
        # Join threads automatically
        await thread.join()
