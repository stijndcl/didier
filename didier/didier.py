import os

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
        await self._load_initial_cogs()
        await self._load_directory_cogs("didier/cogs")

    @property
    def db_session(self) -> AsyncSession:
        """Obtain a database session"""
        return DBSession()

    async def on_ready(self):
        """Event triggered when the bot is ready"""
        print(settings.DISCORD_READY_MESSAGE)

    async def _load_initial_cogs(self):
        """Load all cogs"""
        for extension in self.initial_extensions:
            await self.load_extension(f"didier.cogs.{extension}")

    async def _load_directory_cogs(self, path: str):
        """Load all cogs in a given directory"""
        load_path = path.removeprefix("./").replace("/", ".")

        for file in os.listdir(path):
            if file.endswith(".py") and not file.startswith("_") and not file.startswith(self.initial_extensions):
                await self.load_extension(f"{load_path}.{file[:-3]}")
            elif os.path.isdir(new_path := f"{path}/{file}"):
                await self._load_directory_cogs(new_path)
