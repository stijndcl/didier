import traceback

from discord.ext import commands, tasks  # type: ignore # Strange & incorrect Mypy error

import settings
from database.crud.ufora_announcements import remove_old_announcements
from didier import Didier
from didier.data.embeds.ufora.announcements import fetch_ufora_announcements


class Tasks(commands.Cog):
    """Task loops that run periodically"""

    client: Didier

    def __init__(self, client: Didier):
        # pylint: disable=no-member
        self.client = client

        # Only pull announcements if a token was provided
        if settings.UFORA_RSS_TOKEN is not None and settings.UFORA_ANNOUNCEMENTS_CHANNEL is not None:
            self.pull_ufora_announcements.start()
            self.remove_old_ufora_announcements.start()

    @tasks.loop(minutes=10)
    async def pull_ufora_announcements(self):
        """Task that checks for new Ufora announcements & logs them in a channel"""
        # In theory this shouldn't happen but just to please Mypy
        if settings.UFORA_RSS_TOKEN is None or settings.UFORA_ANNOUNCEMENTS_CHANNEL is None:
            return

        async with self.client.db_session as db_session:
            announcements_channel = self.client.get_channel(settings.UFORA_ANNOUNCEMENTS_CHANNEL)
            announcements = await fetch_ufora_announcements(self.client.http_session, db_session)

            for announcement in announcements:
                await announcements_channel.send(embed=announcement.to_embed())

    @pull_ufora_announcements.before_loop
    async def _before_ufora_announcements(self):
        """Don't try to get announcements if the bot isn't ready yet"""
        await self.client.wait_until_ready()

    @pull_ufora_announcements.error
    async def _on_announcements_error(self, error: BaseException):
        """Error handler for the Ufora Announcements task"""
        print("".join(traceback.format_exception(type(error), error, error.__traceback__)))

    @tasks.loop(hours=24)
    async def remove_old_ufora_announcements(self):
        """Remove all announcements that are over 1 week old, once per day"""
        async with self.client.db_session as session:
            await remove_old_announcements(session)

    @remove_old_ufora_announcements.before_loop
    async def _before_remove_old_ufora_announcements(self):
        await self.client.wait_until_ready()


async def setup(client: Didier):
    """Load the cog"""
    await client.add_cog(Tasks(client))
