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
    async def poke(self, ctx, member=None):
        if not await self.pokeChecks(ctx):
            return

        member = ctx.message.mentions[0]
        await ctx.send("**{}** heeft **{}** getikt. **{}** is hem!".format(
            ctx.author.display_name, member.display_name, member.display_name))

        # Add into the database
        poke.update(ctx.author.id, member.id)
        stats.update(member.id, "poked", int(stats.getOrAddUser(member.id)[1]) + 1)

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

    async def pokeChecks(self, ctx):
        if len(ctx.message.mentions) == 0:
            await ctx.send("Dit is geen geldige persoon.")
            return False
        if len(ctx.message.mentions) > 1:
            await ctx.send("Je kan maar 1 persoon tegelijk tikken.")
            return False
        if ctx.message.mentions[0].id == ctx.author.id:
            await ctx.send("Je kan jezelf niet tikken, {}.".format(ctx.author.display_name))
            return False
        if ctx.message.mentions[0].id == self.client.user.id:
            await ctx.send("Je kan me niet tikken, {}.".format(ctx.author.display_name))
            return False
        if str(ctx.message.mentions[0].id) in constants.botIDs:
            await ctx.send("Je kan geen bots tikken, {}.".format(ctx.author.display_name))
            return False

        # Check database things
        p = poke.get()
        if str(p[0]) != str(ctx.author.id):
            await ctx.send("Het is niet jouw beurt, {}.".format(ctx.author.display_name))
            return False
        if str(ctx.message.mentions[0].id) == str(p[2]):
            await ctx.send("Je mag niet terugtikken, {}.".format(ctx.author.display_name))
            return False
        if poke.blacklisted(ctx.message.mentions[0].id):
            await ctx.send("Deze persoon heeft zichzelf geblacklisted en kan niet meer getikt worden.")
            return False

        return True


def setup(client):
    client.add_cog(Poke(client))
