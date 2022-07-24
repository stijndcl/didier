import discord
from discord.ext import commands

from database.crud import birthdays
from didier import Didier
from didier.utils.types.datetime import str_to_date
from didier.utils.types.string import leading


class Discord(commands.Cog):
    """Cog for commands related to Discord, servers, and members"""

    client: Didier

    def __init__(self, client: Didier):
        self.client = client

    @commands.group(name="Birthday", aliases=["Bd", "Birthdays"], case_insensitive=True, invoke_without_command=True)
    async def birthday(self, ctx: commands.Context, user: discord.User = None):
        """Command to check the birthday of a user"""
        user_id = (user and user.id) or ctx.author.id
        async with self.client.db_session as session:
            birthday = await birthdays.get_birthday_for_user(session, user_id)

        name = "Jouw" if user is None else f"{user.display_name}'s"

        if birthday is None:
            return await ctx.reply(f"{name} verjaardag zit niet in de database.", mention_author=False)

        day, month = leading("0", str(birthday.birthday.day)), leading("0", str(birthday.birthday.month))

        return await ctx.reply(f"{name} verjaardag staat ingesteld op **{day}/{month}**.", mention_author=False)

    @birthday.command(name="Set", aliases=["Config"])
    async def birthday_set(self, ctx: commands.Context, date_str: str):
        """Command to set your birthday"""
        try:
            default_year = 2001
            date = str_to_date(date_str, formats=["%d/%m/%Y", "%d/%m/%y", "%d/%m"])

            # If no year was passed, make it 2001 by default
            if date_str.count("/") == 1:
                date.replace(year=default_year)

        except ValueError:
            return await ctx.reply(f"`{date_str}` is geen geldige datum.", mention_author=False)

        async with self.client.db_session as session:
            await birthdays.add_birthday(session, ctx.author.id, date)
            await self.client.confirm_message(ctx.message)

    @commands.command(name="Join", usage="[Thread]")
    async def join(self, ctx: commands.Context, thread: discord.Thread):
        """Make Didier join a thread"""
        if thread.me is not None:
            return await ctx.reply()


async def setup(client: Didier):
    """Load the cog"""
    await client.add_cog(Discord(client))
