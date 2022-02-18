import discord

from data import constants
import datetime
from decorators import help
from discord.ext import commands
from enums.help_categories import Category
from functions import checks, timeFormatters
from functions.database import poke, stats


class Poke(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.utilsCog = self.client.get_cog("Utils")

    # Don't allow any commands to work when locked
    def cog_check(self, ctx):
        return not self.client.locked

    @commands.group(name="Poke", usage="[@Persoon]", case_insensitive=True, invoke_without_command=True)
    @commands.check(checks.allowedChannels)
    @help.Category(category=Category.Games)
    async def poke(self, ctx, poked: discord.Member = None):
        if not await self.pokeChecks(ctx, poked):
            return

        await ctx.send("**{}** heeft **{}** getikt. **{}** is hem!".format(
            ctx.author.display_name, poked.display_name, poked.display_name))

        # Add into the database
        poke.update(ctx.author.id, poked.id)
        stats.update(poked.id, "poked", int(stats.getOrAddUser(poked.id)[1]) + 1)

    @poke.command(name="Blacklist", aliases=["Bl"])
    async def blacklist(self, ctx):
        if poke.blacklisted(ctx.author.id):
            await ctx.send("Je hebt jezelf al geblacklisted, {}.".format(ctx.author.display_name))
            return
        if str(poke.get()[0]) == str(ctx.author.id):
            await ctx.send("Je kan jezelf niet blacklisten als je aan de beurt bent, {}.".format(
                ctx.author.display_name))
            return
        poke.blacklist(ctx.author.id)
        await ctx.send("**{}** heeft zichzelf geblacklisted en kan niet meer getikt worden.".format(
            ctx.author.display_name))

    @poke.command(aliases=["wl"], hidden=True)
    async def whitelist(self, ctx, *user):
        user = ctx.message.mentions[0].id
        if not poke.blacklisted(user):
            await ctx.send("Deze persoon is niet geblacklisted.")
            return

        poke.blacklist(user, False)
        await ctx.send("**{}** heeft {} gewhitelisted.".format(
            ctx.author.display_name, self.utilsCog.getDisplayName(ctx, user)))

    @poke.command(name="Current")
    async def current(self, ctx):
        p = poke.get()
        pokedTimeStamp = timeFormatters.epochToDate(int(p[1]))["dateDT"]
        timeString = timeFormatters.diffDayBasisString(pokedTimeStamp)

        await ctx.send("Het is al **{}** aan **{}**.".format(timeString, self.utilsCog.getDisplayName(ctx, p[0])))

    @poke.command(hidden=True)
    async def me(self, ctx):
        await ctx.send("Liever niet.")

    @poke.command(hidden=True)
    @commands.check(checks.isMe)
    async def reset(self, ctx):
        new = poke.reset()
        await ctx.send("Poke is gereset. <@!{}> is hem!".format(str(new)))

    @poke.command(aliases=["Lb", "Leaderboards"], hidden=True)
    async def leaderboard(self, ctx):
        await self.client.get_cog("Leaderboards").callLeaderboard("poke", ctx)

    async def pokeChecks(self, ctx, poked: discord.Member = None):
        # no mentions
        if poked is None:
            await ctx.send("Dit is geen geldige persoon.")
            return None

        # author poking themselves
        print(f"Poked: {poked}, author: {ctx.author}")
        if poked == ctx.author:
            await ctx.send("Je kan jezelf niet tikken, {}.".format(ctx.author.display_name))
            return False

        # author poking didier
        if poked == self.client.user:
            await ctx.send("Je kan me niet tikken, {}.".format(ctx.author.display_name))
            return False

        # author poking bots
        if poked.bot:
            await ctx.send("Je kan geen bots tikken, {}.".format(ctx.author.display_name))
            return False

        # Check database things
        p = poke.get()

        # author poking outside their turn
        if str(p[0]) != str(ctx.author.id):
            await ctx.send("Het is niet jouw beurt, {}.".format(ctx.author.display_name))
            return False

        # author poking back
        if poked.id == str(p[2]):
            await ctx.send("Je mag niet terugtikken, {}.".format(ctx.author.display_name))
            return False

        # author poking someone who wishes not to be poked
        if poke.blacklisted(poked):
            await ctx.send("Deze persoon heeft zichzelf geblacklisted en kan niet meer getikt worden.")
            return False

        return True


def setup(client):
    client.add_cog(Poke(client))
