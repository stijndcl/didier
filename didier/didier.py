import os
import sys
import traceback
from typing import Union, Optional

import discord
from discord.ext import commands
from sqlalchemy.ext.asyncio import AsyncSession

import settings
from database.engine import DBSession
from didier.utils.prefix import get_prefix


class Didier(commands.Bot):
    """DIDIER <3"""

    initial_extensions: tuple[str] = ()

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

    async def setup_hook(self) -> None:
        """Hook called once the bot is initialised"""
        # Load extensions
        await self._load_initial_extensions()
        await self._load_directory_extensions("didier/cogs")

        # Sync application commands to the test guild
        for guild in settings.DISCORD_TEST_GUILDS:
            guild_object = discord.Object(id=guild)

            self.tree.copy_global_to(guild=guild_object)
            await self.tree.sync(guild=guild_object)

    @property
    def db_session(self) -> AsyncSession:
        """Obtain a database session"""
        return DBSession()

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

    async def respond(
        self,
        context: Union[commands.Context, discord.Interaction],
        message: str,
        mention_author: bool = False,
        ephemeral: bool = True,
        embeds: Optional[list[discord.Embed]] = None,
    ):
        """Function to respond to both a normal message and an interaction"""
        if isinstance(context, commands.Context):
            return await context.reply(message, mention_author=mention_author, embeds=embeds)

        if isinstance(context, discord.Interaction):
            return await context.response.send_message(message, ephemeral=ephemeral, embeds=embeds)

    async def resolve_message(self, reference: discord.MessageReference) -> discord.Message:
        """Fetch a message from a reference"""
        # Message is in the cache, return it
        if reference.cached_message is not None:
            return reference.cached_message

        # For older messages: fetch them from the API
        channel = self.get_channel(reference.channel_id)
        return await channel.fetch_message(reference.message_id)

    async def on_ready(self):
        """Event triggered when the bot is ready"""
        print(settings.DISCORD_READY_MESSAGE)

    async def on_command_error(self, context: commands.Context, exception: commands.CommandError, /) -> None:
        """Event triggered when a regular command errors"""
        # If developing, print everything to stdout so you don't have to
        # check the logs all the time
        if settings.SANDBOX:
            print(traceback.format_exc(), file=sys.stderr)
            return
