import discord
from discord import Message
from discord.ext import commands
from sqlalchemy.ext.asyncio import AsyncSession

import settings
from database.engine import DBSession
from didier.utils.prefix import get_prefix


class Didier(commands.Bot):
    """DIDIER <3"""

    def __init__(self):
        activity = discord.Activity(type=discord.ActivityType.playing, name=settings.DISCORD_STATUS_MESSAGE)
        status = discord.Status.online

        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True

        super().__init__(
            command_prefix=get_prefix, case_insensitive=True, intents=intents, activity=activity, status=status
        )

    @property
    def db_session(self) -> AsyncSession:
        """Obtain a database session"""
        return DBSession()

    async def on_ready(self):
        """Event triggered when the bot is ready"""
        print(settings.DISCORD_READY_MESSAGE)

    async def on_message(self, message: Message, /) -> None:
        print(message.content)
