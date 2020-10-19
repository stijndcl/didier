from converters.numbers import Abbreviated, abbreviated
from data import constants
from decorators import help
import discord
from discord.ext import commands
from enums.help_categories import Category
from enums.numbers import Numbers
from functions import checks
from functions.database import currency, prison, stats
from functions.numbers import getRep
import json
import math
import random


def calcCapacity(level):
    """
    Function that calculates the rob capacity for a given level.
    :param level: the level of the user
    :return: the capacity the user can rob (float)
    """
    cap = 200
    for x in range(level):
        cap *= (math.pow(1.03, x))
    return round(cap)


class Dinks(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.utilsCog = self.client.get_cog("Utils")

    # Don't allow any commands to work when locked
    def cog_check(self, ctx):
        return not self.client.locked

    @commands.command(name="Award", aliases=["Reward"], usage="[@Persoon] [Aantal]", hidden=True)
    @commands.check(checks.isMe)
    @help.Category(category=Category.Mod)
    async def award(self, ctx, user: discord.User, amount: Abbreviated):
        """
        Command that awards a user a certain amount of Didier Dinks.
        :param ctx: Discord Context
        :param user: the user to give the Didier Dinks to
        :param amount: the amount of Didier Dinks to award [user]
        """
        # No amount was passed
        if amount is None:
            return

        # Update the db
        currency.update(user.id, "dinks", float(currency.dinks(user.id)) + float(amount))

        # Gets the abbreviated representation of the amount
        rep = getRep(amount, Numbers.t.value)

        await ctx.send("**{}** heeft **{}** zowaar **{}** Didier Dink{} beloond!"
                       .format(ctx.author.display_name, self.utilsCog.getDisplayName(ctx, user.id), rep, checks.pluralS(amount)))

    @commands.group(name="Dinks", aliases=["Cash"], case_insensitive=True, invoke_without_command=True)
    @commands.check(checks.allowedChannels)
    @help.Category(category=Category.Currency)
    async def dinks(self, ctx):
        """
        Command that shows the user's Didier Dinks & Platinum Dinks
        :param ctx: Discord Context
        """
        dinks = currency.dinksAll(ctx.author.id)

        answer = "**{}** heeft **{:,}** Didier Dink{}"\
            .format(ctx.author.display_name, math.floor(dinks["dinks"]), checks.pluralS(dinks["dinks"]))

        if dinks["platinum"] > 0:
            answer += " en **{}** Platinum Dink{}".format(dinks["platinum"], checks.pluralS(dinks["platinum"]))

        await ctx.send(answer + "!")

    @dinks.command(aliases=["Lb", "Leaderboards"], hidden=True)
    @commands.check(checks.allowedChannels)
    async def leaderboard(self, ctx):
        """
        Command that shows the Didier Dinks Leaderboard.
        Alias for Lb Dinks.
        :param ctx: Discord Context
        """
        await self.client.get_cog("Leaderboards").callLeaderboard("dinks", ctx)

    @commands.command(name="Nightly")
    @commands.check(checks.allowedChannels)
    @help.Category(category=Category.Currency)
    async def nightly(self, ctx):
        """
        Command to claim daily Didier Dinks.
        :param ctx: Discord Context
        """
        response = currency.nightly(int(ctx.author.id))
        if response[0]:
            # Claim successful
            await ctx.send("Je hebt je dagelijkse **{:,}** Didier Dinks geclaimt. :fire:**{}**".format(
                response[1], response[2]))
        else:
            # Already claimed today, react PIPO
            await ctx.send("Je kan dit niet meerdere keren per dag doen.")
            reactCog = self.client.get_cog("ReactWord")
            await reactCog.react(ctx, "pipo")

    @commands.command(name="Give", aliases=["Gift"], usage="[@Persoon] [Aantal]")
    @commands.check(checks.allowedChannels)
    @help.Category(category=Category.Currency)
    async def give(self, ctx, person: discord.Member, amount: Abbreviated):
        """
        Command that gives your Didier Dinks to another user.
        :param ctx: Discord Context
        :param person: user to give the Didier Dinks to
        :param amount: the amount of Didier Dinks to give
        """
        # Invalid amount
        if amount is None:
            return

        # Disable DM abuse
        if ctx.guild is None:
            return await ctx.send("Muttn")

        valid = checks.isValidAmount(ctx, amount)
        if not valid[0]:
            return await ctx.send(valid[1])

        amount = float(valid[1])

        currency.update(ctx.author.id, "dinks", float(currency.dinks(ctx.author.id)) - amount)
        currency.update(person.id, "dinks", float(currency.dinks(person.id)) + amount)

        rep = getRep(math.floor(amount), Numbers.t.value)

        await ctx.send("**{}** heeft **{}** zowaar **{}** Didier Dink{} geschonken!"
                       .format(ctx.author.display_name, person.display_name,
                               rep, checks.pluralS(amount)))

    @commands.group(name="Bank", aliases=["B"], case_insensitive=True, invoke_without_command=True)
    @commands.check(checks.allowedChannels)
    @help.Category(category=Category.Currency)
    async def bank(self, ctx):
        """
        Command that shows the user's Didier Bank.
        :param ctx: Discord Context
        """
        # 0  1     2     3              4            5      6       7       8  9       10
        # ID dinks level investedamount investeddays profit defense offense bc nightly streak
        response = currency.getOrAddUser(ctx.author.id)

        # Calculate the cost to level your bank
        interestLevelPrice = round(math.pow(1.28, int(response[2])) * 300)
        ratio = round(float(1 * (1 + (int(response[2]) * 0.01))), 4)

        # Calculate the amount of levels the user can purchase
        counter = 0
        sumPrice = float(math.pow(1.28, int(response[2])) * 300)
        while float(response[1]) + float(response[3]) + float(response[5]) > sumPrice:
            counter += 1
            sumPrice += round(float(math.pow(1.28, int(response[2]) + counter) * 300), 4)
        maxLevels = "" if counter == 0 else " (+{})".format(str(counter))

        embed = discord.Embed(colour=discord.Colour.blue())
        embed.set_author(name="Bank van {}".format(ctx.author.display_name))
        embed.set_thumbnail(url=str(ctx.author.avatar_url))
        embed.add_field(name="Level:", value=str(response[2]) + maxLevels, inline=True)
        embed.add_field(name="Ratio:", value=str(ratio), inline=True)
        embed.add_field(name="Prijs voor volgend level:", value="{:,}".format(interestLevelPrice), inline=False)
        embed.add_field(name="Momenteel geïnvesteerd:", value="{:,}".format(math.floor(float(response[3]))), inline=False)
        embed.add_field(name="Aantal dagen geïnvesteerd:", value=str(response[4]), inline=True)
        embed.add_field(name="Huidige winst na claim:", value="{:,}".format(math.floor(response[5])), inline=False)
        await ctx.send(embed=embed)

    @bank.command(name="Stats")
    async def stats(self, ctx):
        """
        Command that shows the user's bank stats.
        :param ctx: Discord Context
        """
        response = currency.getOrAddUser(ctx.author.id)

        # Calculate the prices to level stats up
        defense = int(response[6])
        defenseLevelPrice = math.floor(math.pow(1.4, defense) * 365) if defense < 38 else 5 * calcCapacity(defense - 6)
        offense = int(response[7])
        capacity = calcCapacity(offense)
        offenseLevelPrice = math.floor(math.pow(1.5, offense) * 369) if offense < 32 else 5 * capacity

        embed = discord.Embed(colour=discord.Colour.blue())
        embed.set_author(name="Bank van {}".format(ctx.author.display_name))
        embed.add_field(name="Offense:", value=str(offense), inline=True)
        embed.add_field(name="Prijs voor volgend level:", value="{:,}".format(int(offenseLevelPrice)), inline=True)
        embed.add_field(name="Capaciteit:", value="{:,}".format(int(capacity)), inline=True)
        embed.add_field(name="Security:", value=str(defense), inline=True)
        embed.add_field(name="Prijs voor volgend level:", value="{:,}".format(int(defenseLevelPrice)), inline=True)
        await ctx.send(embed=embed)

    @bank.group(name="Upgrade", aliases=["U"], case_insensitive=True, usage="[Categorie]", invoke_without_command=True)
    async def upgrade(self, ctx):
        """
        Command group to upgrade bank stats,
        calling the group itself does nothing.
        :param ctx: Discord Context
        """
        pass

    @upgrade.command(name="Level", aliases=["L"], hidden=True)
    async def level(self, ctx):
        """
        Command that upgrades the user's bank level,
        increasing interest.
        :param ctx: Discord Context
        """
        response = currency.getOrAddUser(ctx.author.id)
        interestLevelPrice = float(math.pow(1.28, int(response[2])) * 300)

        # Check if user has enough Didier Dinks to do this
        if float(response[1]) >= interestLevelPrice:
            currency.update(ctx.author.id, "dinks", float(response[1]) - interestLevelPrice)
            currency.update(ctx.author.id, "banklevel", int(response[2]) + 1)
            await ctx.send("**{}** heeft zijn bank geüpgradet naar level **{}**!"
                           .format(ctx.author.display_name, str(int(response[2]) + 1)))
        else:
            await ctx.send("Je hebt niet genoeg Didier Dinks om dit te doen, **{}**."
                           .format(ctx.author.display_name))

    @upgrade.command(aliases=["Cap", "Capacity", "O", "Offence"], hidden=True)
    async def offense(self, ctx):
        """
        Command that upgrades the user's bank offense,
        increasing capacity & rob chances.
        :param ctx: Discord Context
        """
        response = currency.getOrAddUser(ctx.author.id)

        offense = int(response[7])
        capacity = calcCapacity(offense)
        offenseLevelPrice = math.floor(math.pow(1.5, offense) * 369) if offense < 32 else 5 * capacity

        # Check if user has enough Didier Dinks to do this
        if float(response[1]) >= offenseLevelPrice:
            currency.update(ctx.author.id, "dinks", float(response[1]) - offenseLevelPrice)
            currency.update(ctx.author.id, "offense", int(response[7]) + 1)
            await ctx.send("**{}** heeft de offense van zijn bank geüpgradet naar level **{}**!"
                           .format(ctx.author.display_name, int(response[7]) + 1))
        else:
            await ctx.send("Je hebt niet genoeg Didier Dinks om dit te doen, **{}**."
                           .format(ctx.author.display_name))

    @upgrade.command(aliases=["D", "Defence", "Def", "Security"], hidden=True)
    async def defense(self, ctx):
        """
        Command that upgrades the user's bank defense,
        increasing chance of failed robs by others.
        :param ctx: Discord Context
        """
        response = currency.getOrAddUser(ctx.author.id)
        defense = int(response[6])
        defenseLevelPrice = math.floor(math.pow(1.4, defense) * 365) if defense < 38 else 5 * calcCapacity(defense - 6)

        # Check if user has enough Didier Dinks to do this
        if float(response[1]) >= defenseLevelPrice:
            currency.update(ctx.author.id, "dinks", float(response[1]) - defenseLevelPrice)
            currency.update(ctx.author.id, "defense", int(response[6]) + 1)
            await ctx.send("**{}** heeft de security van zijn bank geüpgradet naar level **{}**!"
                           .format(ctx.author.display_name, int(response[6]) + 1))
        else:
            await ctx.send("Je hebt niet genoeg Didier Dinks om dit te doen, **{}**."
                           .format(ctx.author.display_name))

    @commands.command(name="Invest", aliases=["Deposit"], usage="[Aantal]")
    @commands.check(checks.allowedChannels)
    @help.Category(category=Category.Currency)
    async def invest(self, ctx, *amount: Abbreviated):
        """
        Command that invests Didier Dinks into the user's bank.
        :param ctx: Discord Context
        :param amount: the amount of Didier Dinks to invest
        """
        # Tuples don't support assignment
        amount = list(amount)

        if len(amount) != 1:
            await ctx.send("Geef een geldig bedrag op.")
        elif not checks.isValidAmount(ctx, amount[0])[0]:
            await ctx.send(checks.isValidAmount(ctx, amount[0])[1])
        else:
            user = currency.getOrAddUser(ctx.author.id)
            if amount[0] == "all":
                amount[0] = user[1]

            amount[0] = float(amount[0])
            currency.update(ctx.author.id, "investedamount", float(user[3]) + amount[0])
            currency.update(ctx.author.id, "dinks", float(user[1]) - amount[0])
            await ctx.send("**{}** heeft **{:,}** Didier Dink{} geïnvesteerd!"
                           .format(ctx.author.display_name, math.floor(amount[0]), checks.pluralS(amount[0])))

    @commands.command(name="Claim", usage="[Aantal]*")
    @commands.check(checks.allowedChannels)
    @help.Category(category=Category.Currency)
    async def claim(self, ctx, *args):
        """
        Command that claims profit out of the user's Didier Bank.
        :param ctx:
        :param args:
        :return:
        """
        user = currency.getOrAddUser(ctx.author.id)
        args = list(args)
        claimAll = False

        if len(args) == 0:
            args.append("all")
        if args[0] == "all":
            args[0] = float(user[5])
            claimAll = True

        if not claimAll:
            args[0] = abbreviated(str(args[0]))
            if args[0] is None:
                return await ctx.send("Dit is geen geldig bedrag.")

        try:
            # Checks if it can be parsed to int
            _ = int(args[0])
            args[0] = float(args[0])
            # Can't claim more than you have (or negative amounts)
            if args[0] < 0 or args[0] > float(user[5]):
                raise ValueError

            currency.update(ctx.author.id, "profit", float(user[5]) - args[0])
            currency.update(ctx.author.id, "dinks", float(user[1]) + args[0])
            s = stats.getOrAddUser(ctx.author.id)
            stats.update(ctx.author.id, "profit", float(s[7]) + args[0])

            # If you claim everything, you get your invest back as well & your days reset
            if claimAll:
                currency.update(ctx.author.id, "dinks", float(user[1]) + float(user[3]) + float(user[5]))
                currency.update(ctx.author.id, "investedamount", 0.0)
                currency.update(ctx.author.id, "investeddays", 0)
                await ctx.send("**{}** heeft **{:,}** Didier Dink{} geclaimt!"
                               .format(ctx.author.display_name, math.floor(args[0] + float(user[3])),
                                       checks.pluralS(math.floor(args[0] + float(user[3])))))
            else:
                await ctx.send("**{}** heeft **{:,}** Didier Dink{} geclaimt!".format(
                               ctx.author.display_name, math.floor(args[0]), checks.pluralS(math.floor(args[0]))))

        except ValueError:
            await ctx.send("Geef een geldig bedrag op.")

    @commands.group(name="Rob", usage="[@Persoon]", case_insensitive=True, invoke_without_command=True)
    @commands.check(checks.allowedChannels)
    @help.Category(category=Category.Currency)
    async def rob(self, ctx, target: discord.User):
        """
        Command to rob another user.
        :param ctx: Discord Context
        :param target: the target victim to be robbed
        :return:
        """
        canRob, caller, target = await self.canRob(ctx, target)

        if not canRob:
            return

        threshold = 50 + round(int(target[6]) * 0.7)
        rg = random.randint(0 + int(caller[7]), 100)
        stat = stats.getOrAddUser(ctx.author.id)

        # Rob succeeded
        if rg > threshold:
            capacity = float(calcCapacity(caller[7]))
            remaining = capacity

            # Try robbing out of invest first, then Dinks pouch
            amount = capacity if float(target[3]) >= capacity else float(target[3])
            remaining -= amount
            currency.update(target[0], "investedamount", float(target[3]) - amount)

            # Rob out of Dinks pouch
            if amount != capacity and not float(target[1]) < 1:
                if float(target[1]) >= remaining:
                    amount += remaining
                    currency.update(target[0], "dinks", float(target[1]) - remaining)
                else:
                    amount += float(target[1])
                    currency.update(target[0], "dinks", 0.0)

            # Update db
            currency.update(caller[0], "dinks", float(caller[1]) + amount)
            await ctx.send("**{}** heeft **{:,}** Didier Dink{} gestolen van **{}**!".format(
                ctx.author.display_name, math.floor(amount), checks.pluralS(math.floor(amount)),
                self.utilsCog.getDisplayName(ctx, target[0])
            ))

            stats.update(ctx.author.id, "robs_success", int(stat[2]) + 1)
            stats.update(ctx.author.id, "robs_total", float(stat[4]) + amount)
        else:
            # Rob failed

            # Calculate what happens
            fate = random.randint(1, 10)

            # Leave Dinks behind instead of robbing
            if fate < 8:
                punishment = float(calcCapacity(caller[7]))/2
                prisoned = round(float(caller[1])) < round(punishment)

                # Doesn't have enough Dinks -> prison
                if prisoned:
                    diff = round(punishment - float(caller[1]))
                    punishment = round(float(caller[1]))
                    days = 1 + round(int(caller[7]) // 10)
                    prison.imprison(caller[0], diff, days,
                                    round(round(diff)//days))

                # Update db
                currency.update(target[0], "dinks", float(target[1]) + punishment)
                currency.update(caller[0], "dinks", float(caller[1]) - punishment)
                await ctx.send("**{}** was zo vriendelijk om **{}** zowaar **{:,}** Didier Dink{} te geven!"
                               .format(ctx.author.display_name,
                                       self.utilsCog.getDisplayName(ctx, target[0]),
                                       math.floor(punishment), checks.pluralS(math.floor(punishment))))

                # Can't put this in the previous if- because the value of Punishment changes
                if prisoned:
                    await ctx.send("Je bent naar de gevangenis verplaatst omdat je niet genoeg Didier Dinks had.")
            elif fate == 9:
                # Prison
                totalSum = round(calcCapacity(caller[7]))
                days = 1 + (int(caller[7])//10)

                prison.imprison(caller[0], totalSum, days, totalSum/days)
                await ctx.send("**{}** niet stelen, **{}** niet stelen!\nJe bent naar de gevangenis verplaatst.".format(
                    ctx.author.display_name, ctx.author.display_name
                ))
            else:
                # Escape
                await ctx.send("Je poging is mislukt, maar je kon nog net op tijd vluchten, **{}**.".format(
                    ctx.author.display_name))

            stats.update(ctx.author.id, "robs_failed", int(stat[3]) + 1)

    @rob.command(name="Leaderboard", aliases=["Lb", "Leaderboards"], hidden=True)
    async def rob_leaderboard(self, ctx):
        """
        Command that shows the Rob Leaderboard.
        Alias for Lb Rob.
        :param ctx: Discord Context
        """
        await self.client.get_cog("Leaderboards").callLeaderboard("rob", ctx)

    @rob.command(name="Stats", hidden=True)
    async def rob_stats(self, ctx):
        """
        Command that shows the user's rob stats.
        Alias for Stats Rob.
        :param ctx: Discord Context
        """
        await self.client.get_cog("Stats").callStats("rob", ctx)

    @commands.command(name="Prison", aliases=["Jail"])
    @commands.check(checks.allowedChannels)
    @help.Category(category=Category.Currency)
    async def prison(self, ctx):
        """
        Command that shows how long you have to sit in prison for.
        :param ctx: Discord Context
        """
        user = prison.getUser(ctx.author.id)

        if len(user) == 0:
            await ctx.send("Je zit niet in de gevangenis, **{}**.".format(ctx.author.display_name))
            return

        user = user[0]

        embed = discord.Embed(colour=discord.Colour.blue())
        embed.set_author(name="De Gevangenis")
        embed.add_field(name="Borgsom:", value="{:,}".format(math.floor(user[1])), inline=False)
        embed.add_field(name="Resterende dagen:", value="{}".format((user[2])), inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="Bail")
    @commands.check(checks.allowedChannels)
    @help.Category(Category.Currency)
    async def bail(self, ctx):
        """
        Command to bail yourself out of prison.
        :param ctx: Discord Context
        """
        user = prison.getUser(ctx.author.id)
        if len(user) == 0:
            return await ctx.send("Je zit niet in de gevangenis, **{}**.".format(ctx.author.display_name))

        user = user[0]

        # Check if user can afford this
        valid = checks.isValidAmount(ctx, math.floor(user[1]))
        if not valid[0]:
            return await ctx.send(valid[1])

        dinks = currency.dinks(ctx.author.id)
        prison.remove(ctx.author.id)
        currency.update(ctx.author.id, "dinks", float(dinks) - float(user[1]))
        await ctx.send("**{}** heeft zichzelf vrijgekocht!".format(ctx.author.display_name))

        # Update the user's stats
        s = stats.getOrAddUser(ctx.author.id)
        stats.update(ctx.author.id, "bails", int(s[10]) + 1)

        # Increase the bail in the stats file
        with open("files/stats.json", "r") as fp:
            s = json.load(fp)

        s["rob"]["bail_paid"] += float(user[1])

        with open("files/stats.json", "w") as fp:
            json.dump(s, fp)

    async def canRob(self, ctx, target):
        """
        Function that performs checks to see if a user can rob another user.
        In case the rob is not possible, it already sends an error message to show this.
        Returns the database dictionaries corresponding to these two users as they are
        needed in this function anyways, so it prevents an unnecessary database call
        in the rob command.
        :param ctx: Discord Context
        :param target: the target victim to be robbed
        :return: success: boolean, user1 ("Caller"): tuple, user2 ("Target"): tuple
        """
        # Can't rob in DM's
        if str(ctx.channel.type) == "private":
            await ctx.send("Dat doe je niet, {}.".format(ctx.author.display_name))
            return False, None, None

        # Can't rob bots
        if str(ctx.author.id) in constants.botIDs:
            await ctx.send("Nee.")

        # Can't rob in prison
        if len(prison.getUser(ctx.author.id)) != 0:
            await ctx.send("Je kan niemand bestelen als je in de gevangenis zit.")
            return False, None, None

        # Check the database for these users
        user1 = currency.getOrAddUser(ctx.author.id)
        user2 = currency.getOrAddUser(target.id)

        # Can't rob without Didier Dinks
        if float(user1[1]) < 1.0:
            await ctx.send("Mensen zonder Didier Dinks kunnen niet stelen.")
            return False, None, None

        # Target has no Didier Dinks to rob
        if float(user2[1]) < 1.0 and float(user2[3]) < 1.0:
            await ctx.send("Deze persoon heeft geen Didier Dinks om te stelen.")
            return False, None, None

        # Passed all tests
        return True, user1, user2


def setup(client):
    client.add_cog(Dinks(client))
