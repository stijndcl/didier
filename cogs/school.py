from data import schedule
from decorators import help
import discord
from discord.ext import commands
from enums.help_categories import Category
from functions import config, eten, les
from functions.stringFormatters import capitalize
from functions.timeFormatters import intToWeekday, skip_weekends


class School(commands.Cog):

    def __init__(self, client):
        self.client = client

    # Don't allow any commands to work when locked
    def cog_check(self, ctx):
        return not self.client.locked

    @commands.command(name="Eten", aliases=["Food", "Menu"], usage="[Dag]*")
    # @commands.check(checks.allowedChannels)
    @help.Category(category=Category.School)
    async def eten(self, ctx, *day):
        day_dt = les.find_target_date(day if day else None)
        day_dt = skip_weekends(day_dt)
        day = intToWeekday(day_dt.weekday())

        # Create embed
        menu = eten.etenScript(day)
        embed = discord.Embed(colour=discord.Colour.blue())
        embed.set_author(name="Menu voor {}".format(day))

        if "gesloten" in menu[0].lower():
            embed.description = "Restaurant gesloten"
        else:
            embed.add_field(name="Soep:", value=menu[0], inline=False)
            embed.add_field(name="Hoofdgerechten:", value=menu[1], inline=False)

            if menu[2]:
                embed.add_field(name="Groenten:", value=menu[2], inline=False)

            embed.set_footer(text="Omwille van de coronamaatregelen is er een beperkter aanbod, en kan je enkel nog eten afhalen. Ter plaatse eten is niet meer mogelijk.")
        await ctx.send(embed=embed)

    # @commands.command(name="Les", aliases=["Class", "Classes", "Sched", "Schedule"], usage="[Dag]*")
    # @commands.check(checks.allowedChannels)
    # @help.Category(category=Category.School)
    async def les(self, ctx, day=None):
        date = les.find_target_date(day)

        # Person explicitly requested a weekend-day
        if day is not None and day.lower() in ("morgen", "overmorgen") and date.weekday() > 4:
            return await ctx.send(f"{capitalize(day)} is het weekend.")

        date = skip_weekends(date)

        s = schedule.Schedule(date, int(config.get("year")), int(config.get("semester")), day is not None)

        if s.semester_over:
            return await ctx.send("Het semester is afgelopen.")

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


def setup(client):
    client.add_cog(School(client))
