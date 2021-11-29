from data import schedule
from data.embeds.deadlines import Deadlines
from data.embeds.food import Menu
from decorators import help
import discord
from discord.ext import commands
from enums.help_categories import Category
from functions import config, les
from functions.stringFormatters import capitalize
from functions.timeFormatters import skip_weekends


class School(commands.Cog):

    def __init__(self, client):
        self.client = client

    # Don't allow any commands to work when locked
    def cog_check(self, ctx):
        return not self.client.locked

    @commands.command(name="Eten", aliases=["Food", "Menu"], usage="[Dag]*")
    # @commands.check(checks.allowedChannels)
    @help.Category(category=Category.School)
    async def eten(self, ctx, day: str = None):
        if day is not None:
            day = day.lower()

        embed = Menu(day).to_embed()
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(name="Les", aliases=["Class", "Classes", "Sched", "Schedule"], usage="[Dag]*")
    # @commands.check(checks.allowedChannels)
    @help.Category(category=Category.School)
    async def les(self, ctx, day=None):
        if day is not None:
            day = day.lower()

        date = les.find_target_date(day)

        # Person explicitly requested a weekend-day
        if day is not None and day.lower() in ("morgen", "overmorgen") and date.weekday() > 4:
            return await ctx.send(f"{capitalize(day)} is het weekend.")

        date = skip_weekends(date)

        s = schedule.Schedule(date, int(config.get("year")), int(config.get("semester")), day is not None)

        if s.semester_over:
            return await ctx.send("Het semester is afgelopen.")

        # DM only shows user's own minor
        if ctx.guild is None:
            minor_roles = [*schedule.find_minor(self.client, ctx.author.id)]
            return await ctx.send(embed=s.create_schedule(minor_roles=minor_roles).to_embed())

        return await ctx.send(embed=s.create_schedule().to_embed())

    @commands.command(name="Pin", usage="[Message]")
    @help.Category(category=Category.Other)
    async def pin(self, ctx, message: discord.Message):
        # In case people abuse, check if they're blacklisted
        blacklist = []

        if ctx.author.id in blacklist:
            return

        if message.is_system():
            return await ctx.send("Dus jij wil system messages pinnen?\nMag niet.")

        await message.pin(reason="Didier Pin door {}".format(ctx.author.display_name))
        await ctx.message.add_reaction("✅")

    @commands.command(name="Deadlines", aliases=["dl"])
    @help.Category(category=Category.School)
    async def deadlines(self, ctx):
        await ctx.send(embed=Deadlines().to_embed())


def setup(client):
    client.add_cog(School(client))
