import logging
import os

import discord
import motor.motor_asyncio
from aiohttp import ClientSession
from discord.app_commands import AppCommandError
from discord.ext import commands
from sqlalchemy.ext.asyncio import AsyncSession

import settings
from database.crud import custom_commands
from database.engine import DBSession, mongo_client
from database.utils.caches import CacheManager
from didier.data.embeds.error_embed import create_error_embed
from didier.exceptions import HTTPException, NoMatch
from didier.utils.discord.prefix import get_prefix

__all__ = ["Didier"]


logger = logging.getLogger(__name__)


class Didier(commands.Bot):
    """DIDIER <3"""

    database_caches: CacheManager
    error_channel: discord.abc.Messageable
    initial_extensions: tuple[str, ...] = ()
    http_session: ClientSession
    wordle_words: set[str] = set()

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

        self.tree.on_error = self.on_app_command_error

    @property
    def postgres_session(self) -> AsyncSession:
        """Obtain a session for the PostgreSQL database"""
        return DBSession()

    @property
    def mongo_db(self) -> motor.motor_asyncio.AsyncIOMotorDatabase:
        """Obtain a reference to the MongoDB database"""
        return mongo_client[settings.MONGO_DB]

    async def setup_hook(self) -> None:
        """Do some initial setup

        This hook is called once the bot is initialised
        """
        # Load the Wordle dictionary
        self._load_wordle_words()

        # Initialize caches
        self.database_caches = CacheManager()
        async with self.postgres_session as session:
            await self.database_caches.initialize_caches(session, self.mongo_db)

        # Load extensions
        await self._load_initial_extensions()
        await self._load_directory_extensions("didier/cogs")

        # Create aiohttp session
        self.http_session = ClientSession()

        # Configure channel to send errors to
        if settings.ERRORS_CHANNEL is not None:
            self.error_channel = self.get_channel(settings.ERRORS_CHANNEL)
        else:
            self.error_channel = self.get_user(self.owner_id)

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

    def _load_wordle_words(self):
        """Load the dictionary of Wordle words"""
        with open("files/dictionaries/words-english-wordle.txt", "r") as fp:
            for line in fp:
                self.wordle_words.add(line.strip())

    async def get_reply_target(self, ctx: commands.Context) -> discord.Message:
        """Get the target message that should be replied to

        In case the invoking message is a reply to something, reply to the
        original message instead
        """
        if ctx.message.reference is not None:
            return await self.resolve_message(ctx.message.reference)

        return ctx.message

    async def resolve_message(self, reference: discord.MessageReference) -> discord.Message:
        """Fetch a message from a reference"""
        # Message is in the cache, return it
        if reference.cached_message is not None:
            return reference.cached_message

        # For older messages: fetch them from the API
        channel = self.get_channel(reference.channel_id)
        return await channel.fetch_message(reference.message_id)

    async def confirm_message(self, message: discord.Message):
        """Add a checkmark to a message"""
        await message.add_reaction("✅")

    async def reject_message(self, message: discord.Message):
        """Add an X to a message"""
        await message.add_reaction("❌")

    async def log_error(self, message: str, log_to_discord: bool = True):
        """Send an error message to the logs, and optionally the configured channel"""
        logger.error(message)
        if log_to_discord:
            # TODO pretty embed
            await self.error_channel.send(message)

    async def on_ready(self):
        """Event triggered when the bot is ready"""
        print(settings.DISCORD_READY_MESSAGE)

    async def on_message(self, message: discord.Message, /) -> None:
        """Event triggered when a message is sent"""
        # Ignore messages by bots
        if message.author.bot:
            return

        # Boos react to people that say Dider
        if "dider" in message.content.lower() and message.author.id != self.user.id:
            await message.add_reaction(settings.DISCORD_BOOS_REACT)

        # Potential custom command
        if await self._try_invoke_custom_command(message):
            return

        await self.process_commands(message)

        # TODO easter eggs
        # TODO stats

    async def _try_invoke_custom_command(self, message: discord.Message) -> bool:
        """Check if the message tries to invoke a custom command

        If it does, send the reply associated with it
        Returns a boolean indicating if a message invoked a command or not
        """
        # Doesn't start with the custom command prefix
        if not message.content.startswith(settings.DISCORD_CUSTOM_COMMAND_PREFIX):
            return False

        async with self.postgres_session as session:
            # Remove the prefix
            content = message.content[len(settings.DISCORD_CUSTOM_COMMAND_PREFIX) :]
            command = await custom_commands.get_command(session, content)

            # Command found
            if command is not None:
                await message.reply(command.response, mention_author=False)
                return True

        # Nothing found
        return False

    async def on_thread_create(self, thread: discord.Thread):
        """Event triggered when a new thread is created"""
        await thread.join()

    async def on_app_command_error(self, interaction: discord.Interaction, exception: AppCommandError):
        """Event triggered when an application command errors"""
        # If commands have their own error handler, let it handle the error instead
        if hasattr(interaction.command, "on_error"):
            return

        if isinstance(exception, (NoMatch, discord.app_commands.CommandInvokeError)):
            if interaction.response.is_done():
                return await interaction.response.send_message(str(exception.original), ephemeral=True)
            else:
                return await interaction.followup.send(str(exception.original), ephemeral=True)

    async def on_command_error(self, ctx: commands.Context, exception: commands.CommandError, /):
        """Event triggered when a regular command errors"""
        # If working locally, print everything to your console
        if settings.SANDBOX:
            await super().on_command_error(ctx, exception)
            return

        # If commands have their own error handler, let it handle the error instead
        if hasattr(ctx.command, "on_error"):
            return

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
        if isinstance(exception, commands.CommandInvokeError) and isinstance(
            exception.original,
            (
                NoMatch,
                HTTPException,
            ),
        ):
            return await ctx.reply(str(exception.original), mention_author=False)

        # Print everything that we care about to the logs/stderr
        await super().on_command_error(ctx, exception)

        if isinstance(exception, commands.MessageNotFound):
            return await ctx.reply("This message could not be found.", ephemeral=True, delete_after=10)

        if isinstance(
            exception,
            (
                commands.BadArgument,
                commands.MissingRequiredArgument,
                commands.UnexpectedQuoteError,
                commands.ExpectedClosingQuoteError,
            ),
        ):
            return await ctx.reply("Invalid arguments.", ephemeral=True, delete_after=10)

        if settings.ERRORS_CHANNEL is not None:
            embed = create_error_embed(ctx, exception)
            channel = self.get_channel(settings.ERRORS_CHANNEL)
            await channel.send(embed=embed)
