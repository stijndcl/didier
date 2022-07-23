import datetime
import traceback

from discord.ext import commands, tasks  # type: ignore # Strange & incorrect Mypy error

import settings
from database import enums
from database.crud.ufora_announcements import remove_old_announcements
from didier import Didier
from didier.data.embeds.ufora.announcements import fetch_ufora_announcements
from didier.decorators.tasks import timed_task
from didier.utils.discord.checks import is_owner
from didier.utils.types.datetime import LOCAL_TIMEZONE

# datetime.time()-instances for when every task should run
DAILY_RESET_TIME = datetime.time(hour=0, minute=0, tzinfo=LOCAL_TIMEZONE)
SOCIALLY_ACCEPTABLE_TIME = datetime.time(hour=7, minute=0, tzinfo=LOCAL_TIMEZONE)


class Tasks(commands.Cog):
    """Task loops that run periodically

    Preferably these would use the new `time`-kwarg, but these don't run
    on startup, which is not ideal. This means we still have to run them every hour
    in order to never miss anything if Didier goes offline by coincidence
    """

    client: Didier
    _tasks: dict[str, tasks.Loop]

    def __init__(self, client: Didier):
        self.client = client

        # Only pull announcements if a token was provided
        if settings.UFORA_RSS_TOKEN is not None and settings.UFORA_ANNOUNCEMENTS_CHANNEL is not None:
            self.pull_ufora_announcements.start()
            self.remove_old_ufora_announcements.start()

        # Start all tasks
        self.check_birthdays.start()

        self._tasks = {"birthdays": self.check_birthdays, "ufora": self.pull_ufora_announcements}

    @commands.group(name="Tasks", case_insensitive=True, invoke_without_command=True)
    @commands.check(is_owner)
    async def tasks_group(self, ctx: commands.Context):
        """Command group for Task-related commands

        Invoking the group itself shows the time until the next iteration
        """
        raise NotImplementedError()

    @tasks_group.command(name="Force", case_insensitive=True)
    async def force_task(self, ctx: commands.Context, name: str):
        """Command to force-run a task without waiting for the run time"""
        name = name.lower()
        if name not in self._tasks:
            return await ctx.reply(f"Geen task gevonden voor `{name}`.", mention_author=False)

        task = self._tasks[name]
        await task()

    @tasks.loop(time=SOCIALLY_ACCEPTABLE_TIME)
    @timed_task(enums.TaskType.BIRTHDAYS)
    async def check_birthdays(self):
        """Check if it's currently anyone's birthday"""

    @check_birthdays.before_loop
    async def _before_check_birthdays(self):
        await self.client.wait_until_ready()

    @tasks.loop(minutes=10)
    @timed_task(enums.TaskType.UFORA_ANNOUNCEMENTS)
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
        await self.client.wait_until_ready()

    @tasks.loop(hours=24)
    async def remove_old_ufora_announcements(self):
        """Remove all announcements that are over 1 week old, once per day"""
        async with self.client.db_session as session:
            await remove_old_announcements(session)

    @check_birthdays.error
    @pull_ufora_announcements.error
    @remove_old_ufora_announcements.error
    async def _on_tasks_error(self, error: BaseException):
        """Error handler for all tasks"""
        print("".join(traceback.format_exception(type(error), error, error.__traceback__)))


async def setup(client: Didier):
    """Load the cog"""
    await client.add_cog(Tasks(client))
