import traceback

from discord.ext import commands, tasks

import settings
from didier import Didier
from didier.data.embeds.ufora.announcements import fetch_ufora_announcements


# TODO task to clean up old announcements? (> 1 week)
class Tasks(commands.Cog):
    """Task loops that run periodically"""

    client: Didier

    def __init__(self, client: Didier):
        self.client = client

        # Only pull announcements if a token was provided
        if settings.UFORA_RSS_TOKEN is not None and settings.UFORA_ANNOUNCEMENTS_CHANNEL is not None:
            self.pull_ufora_announcements.start()  # pylint: disable=no-member

    @tasks.loop(minutes=10)
    async def pull_ufora_announcements(self):
        """Task that checks for new Ufora announcements & logs them in a channel"""
        # In theory this shouldn't happen but just to please Mypy
        if settings.UFORA_RSS_TOKEN is None or settings.UFORA_ANNOUNCEMENTS_CHANNEL is None:
            return

        announcements_channel = self.client.get_channel(settings.UFORA_ANNOUNCEMENTS_CHANNEL)
        announcements = await fetch_ufora_announcements(self.client.db_session)

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


async def setup(client: Didier):
    """Load the cog"""
    await client.add_cog(Tasks(client))
