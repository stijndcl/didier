import discord
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
