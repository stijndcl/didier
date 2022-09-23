import datetime
import random
import traceback

import discord
from discord.ext import commands, tasks  # type: ignore # Strange & incorrect Mypy error
from overrides import overrides

import settings
from database import enums
from database.crud.birthdays import get_birthdays_on_day
from database.crud.reminders import get_all_reminders_for_category
from database.crud.ufora_announcements import remove_old_announcements
from database.crud.wordle import set_daily_word
from database.schemas import Reminder
from didier import Didier
from didier.data.embeds.schedules import (
    Schedule,
    get_schedule_for_day,
    parse_schedule_from_content,
)
from didier.data.embeds.ufora.announcements import fetch_ufora_announcements
from didier.decorators.tasks import timed_task
from didier.utils.discord.checks import is_owner
from didier.utils.types.datetime import LOCAL_TIMEZONE, tz_aware_now

# datetime.time()-instances for when every task should run
DAILY_RESET_TIME = datetime.time(hour=0, minute=0, tzinfo=LOCAL_TIMEZONE)
SOCIALLY_ACCEPTABLE_TIME = datetime.time(hour=7, minute=0, tzinfo=LOCAL_TIMEZONE)


# TODO more messages?
BIRTHDAY_MESSAGES = ["Gelukkige verjaardag {mention}!", "Happy birthday {mention}!"]


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

        self._tasks = {
            "birthdays": self.check_birthdays,
            "schedules": self.pull_schedules,
            "reminders": self.reminders,
            "ufora": self.pull_ufora_announcements,
            "remove_ufora": self.remove_old_ufora_announcements,
            "wordle": self.reset_wordle_word,
        }

    @overrides
    def cog_load(self) -> None:
        # Only check birthdays if there's a channel to send it to
        if settings.BIRTHDAY_ANNOUNCEMENT_CHANNEL is not None:
            self.check_birthdays.start()

        # Only pull announcements if a token was provided
        if settings.UFORA_RSS_TOKEN is not None and settings.UFORA_ANNOUNCEMENTS_CHANNEL is not None:
            self.pull_ufora_announcements.start()
            self.remove_old_ufora_announcements.start()

        # Start other tasks
        self.reminders.start()
        self.reset_wordle_word.start()
        self.pull_schedules.start()

    @overrides
    def cog_unload(self) -> None:
        # Cancel all pending tasks
        for task in self._tasks.values():
            if task.is_running():
                task.stop()

    @commands.group(name="Tasks", aliases=["Task"], case_insensitive=True, invoke_without_command=True)
    @commands.check(is_owner)
    async def tasks_group(self, ctx: commands.Context):
        """Command group for Task-related commands

        Invoking the group itself shows the time until the next iteration
        """
        embed = discord.Embed(colour=discord.Colour.blue(), title="Tasks")

        for name, task in self._tasks.items():
            next_iter = task.next_iteration
            timestamp = f"<t:{round(next_iter.timestamp())}:R>" if next_iter is not None else "N/A"
            embed.add_field(name=name, value=timestamp)

        await ctx.reply(embed=embed, mention_author=False)

    @tasks_group.command(name="Force", case_insensitive=True, usage="[Task]")
    async def force_task(self, ctx: commands.Context, name: str):
        """Command to force-run a task without waiting for the specified run time"""
        name = name.lower()
        if name not in self._tasks:
            return await ctx.reply(f"Found no tasks matching `{name}`.", mention_author=False)

        task = self._tasks[name]
        await task(forced=True)
        await self.client.confirm_message(ctx.message)

    @tasks.loop(time=SOCIALLY_ACCEPTABLE_TIME)
    @timed_task(enums.TaskType.BIRTHDAYS)
    async def check_birthdays(self, **kwargs):
        """Check if it's currently anyone's birthday"""
        _ = kwargs

        now = tz_aware_now().date()
        async with self.client.postgres_session as session:
            birthdays = await get_birthdays_on_day(session, now)

        channel = self.client.get_channel(settings.BIRTHDAY_ANNOUNCEMENT_CHANNEL)
        if channel is None:
            return await self.client.log_error("Unable to find channel for birthday announcements")

        for birthday in birthdays:
            user = self.client.get_user(birthday.user_id)

            await channel.send(random.choice(BIRTHDAY_MESSAGES).format(mention=user.mention))

    @check_birthdays.before_loop
    async def _before_check_birthdays(self):
        await self.client.wait_until_ready()

    @tasks.loop(time=DAILY_RESET_TIME)
    @timed_task(enums.TaskType.SCHEDULES)
    async def pull_schedules(self, **kwargs):
        """Task that pulls the schedules & saves the files locally

        Schedules are then parsed & cached in memory
        """
        _ = kwargs

        new_schedules: dict[settings.ScheduleType, Schedule] = {}

        async with self.client.postgres_session as session:
            for data in settings.SCHEDULE_DATA:
                if data.schedule_url is None:
                    continue

                async with self.client.http_session.get(data.schedule_url) as response:
                    # If a schedule couldn't be fetched, log it and move on
                    if response.status != 200:
                        await self.client.log_warning(
                            f"Unable to fetch schedule {data.name} (status {response.status}).", log_to_discord=False
                        )
                        continue

                    # Write the content to a file
                    content = await response.text()
                    with open(f"files/schedules/{data.name}.ics", "w+") as fp:
                        fp.write(content)

                    schedule = await parse_schedule_from_content(content, database_session=session)
                    if schedule is None:
                        continue

                    new_schedules[data.name] = schedule

        # Only replace cached version if all schedules succeeded
        self.client.schedules = new_schedules

    @tasks.loop(minutes=10)
    @timed_task(enums.TaskType.UFORA_ANNOUNCEMENTS)
    async def pull_ufora_announcements(self, **kwargs):
        """Task that checks for new Ufora announcements & logs them in a channel"""
        _ = kwargs

        # In theory this shouldn't happen but just to please Mypy
        if settings.UFORA_RSS_TOKEN is None or settings.UFORA_ANNOUNCEMENTS_CHANNEL is None:
            return

        async with self.client.postgres_session as db_session:
            announcements_channel = self.client.get_channel(settings.UFORA_ANNOUNCEMENTS_CHANNEL)
            announcements = await fetch_ufora_announcements(self.client.http_session, db_session)

            for announcement in announcements:
                await announcements_channel.send(embed=announcement.to_embed())

    @pull_ufora_announcements.before_loop
    async def _before_ufora_announcements(self):
        await self.client.wait_until_ready()

    async def _send_les_reminders(self, entries: list[Reminder]):
        today = datetime.date(year=2022, month=9, day=26)

        # Create the main schedule for the day once here, to avoid doing it repeatedly
        daily_schedule = get_schedule_for_day(self.client, today)

        # No class today
        if not daily_schedule:
            return

        for entry in entries:
            member = self.client.main_guild.get_member(entry.user_id)
            if not member:
                continue

            roles = {role.id for role in member.roles}
            personal_schedule = daily_schedule.personalize(roles)

            # No class today
            if not personal_schedule:
                continue

            await member.send(embed=personal_schedule.to_embed(day=today))

    # @tasks.loop(time=SOCIALLY_ACCEPTABLE_TIME)
    @tasks.loop(hours=3)
    async def reminders(self, **kwargs):
        """Send daily reminders to people"""
        _ = kwargs

        async with self.client.postgres_session as session:
            for category in enums.ReminderCategory:
                entries = await get_all_reminders_for_category(session, category)
                if not entries:
                    continue

                # This is slightly ugly, but it's the best way to go about it
                # There won't be a lot of categories anyway
                if category == enums.ReminderCategory:
                    await self._send_les_reminders(entries)

    @reminders.before_loop
    async def _before_reminders(self):
        await self.client.wait_until_ready()

    @tasks.loop(hours=24)
    async def remove_old_ufora_announcements(self):
        """Remove all announcements that are over 1 week old, once per day"""
        async with self.client.postgres_session as session:
            await remove_old_announcements(session)

    @tasks.loop(time=DAILY_RESET_TIME)
    async def reset_wordle_word(self, forced: bool = False):
        """Reset the daily Wordle word"""
        async with self.client.postgres_session as session:
            await set_daily_word(session, random.choice(tuple(self.client.wordle_words)), forced=forced)
            await self.client.database_caches.wordle_word.invalidate(session)

    @reset_wordle_word.before_loop
    async def _before_reset_wordle_word(self):
        await self.client.wait_until_ready()

    @check_birthdays.error
    @pull_schedules.error
    @pull_ufora_announcements.error
    @reminders.error
    @remove_old_ufora_announcements.error
    @reset_wordle_word.error
    async def _on_tasks_error(self, error: BaseException):
        """Error handler for all tasks"""
        print("".join(traceback.format_exception(type(error), error, error.__traceback__)))
        self.client.dispatch("task_error")


async def setup(client: Didier):
    """Load the cog

    Initially fetch the wordle word from the database, or reset it
    if there hasn't been a reset yet today
    """
    cog = Tasks(client)
    await client.add_cog(cog)
    await cog.reset_wordle_word()
