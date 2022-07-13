import os

import discord
from aiohttp import ClientSession
from discord.ext import commands
from sqlalchemy.ext.asyncio import AsyncSession

import settings
from database.crud import custom_commands
from database.engine import DBSession
from didier.utils.discord.prefix import get_prefix

__all__ = ["Didier"]


class Didier(commands.Bot):
    """DIDIER <3"""

    initial_extensions: tuple[str, ...] = ()
    http_session: ClientSession

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

    @property
    def db_session(self) -> AsyncSession:
        """Obtain a database session"""
        return DBSession()

    async def setup_hook(self) -> None:
        """Do some initial setup

        This hook is called once the bot is initialised
        """
        # Load extensions
        await self._load_initial_extensions()
        await self._load_directory_extensions("didier/cogs")

        # Create aiohttp session
        self.http_session = ClientSession()

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

    async def _try_invoke_custom_command(self, message: discord.Message) -> bool:
        """Check if the message tries to invoke a custom command

        If it does, send the reply associated with it
        Returns a boolean indicating if a message invoked a command or not
        """
        # Doesn't start with the custom command prefix
        if not message.content.startswith(settings.DISCORD_CUSTOM_COMMAND_PREFIX):
            return False

        async with self.db_session as session:
            # Remove the prefix
            content = message.content[len(settings.DISCORD_CUSTOM_COMMAND_PREFIX) :]
            command = await custom_commands.get_command(session, content)

            # Command found
            if command is not None:
                await message.reply(command.response, mention_author=False)
                return True

        # Nothing found
        return False

    async def on_command_error(self, context: commands.Context, exception: commands.CommandError, /) -> None:
        """Event triggered when a regular command errors"""
        # Print everything to the logs/stderr
        await super().on_command_error(context, exception)

        # If developing, do nothing special
        if settings.SANDBOX:
            return
