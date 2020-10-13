from converters.numbers import Abbreviated, abbreviated
from decorators import help
import discord
from discord.ext import commands
from enums.help_categories import Category
from functions import checks, dinks
from functions.database import currency, stats
import json
import math
import random


class Games(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Don't allow any commands to work when locked
    def cog_check(self, ctx):
        return not self.client.locked

    @commands.group(name="Coinflip", aliases=["Cf"], usage="[Inzet]* [Aantal]*", case_insensitive=True, invoke_without_command=True)
    @commands.check(checks.allowedChannels)
    @help.Category(category=Category.Gamble)
    async def coinflip(self, ctx, *args):
        """
        Command to flip a coin, optionally for Didier Dinks.
        :param ctx: Discord Context
        :param args: bet & wager
        """
        args = list(args)
        choices = ["Kop", "Munt"]
        result = random.choice(choices)

        # No choice made & no wager
        if len(args) == 0:
            await ctx.send("**{}**!".format(result))
            self.updateStats("cf", "h" if result == "Kop" else "t")
            return

        # Check for invalid args
        if len(args) == 1 or args[0][0].lower() not in "kmht":
            return await ctx.send("Controleer je argumenten.")

        args[1] = abbreviated(args[1])
        valid = checks.isValidAmount(ctx, args[1])

        # Invalid amount
        if not valid[0]:
            return await ctx.send(valid[1])

        # Allow full words, abbreviations, and English alternatives
        args[0] = "k" if args[0][0].lower() == "k" or args[0][0].lower() == "h" else "m"
        won = await self.gamble(ctx, args[0], result, valid[1], 2)

        if won:
            s = stats.getOrAddUser(ctx.author.id)
            stats.update(ctx.author.id, "cf_wins", int(s[8]) + 1)
            stats.update(ctx.author.id, "cf_profit", float(s[9]) + float(valid[1]))

        self.updateStats("cf", "h" if result == "Kop" else "t")

    @coinflip.command(name="Stats", hidden=True)
    async def cf_stats(self, ctx):
        return await self.client.get_cog("Stats").callStats("cf", ctx)

    @commands.group(name="Dice", aliases=["Roll"], usage="[Inzet]* [Aantal]*", case_insensitive=True, invoke_without_command=True)
    @commands.check(checks.allowedChannels)
    @help.Category(category=Category.Gamble)
    async def dice(self, ctx, *args):
        """
        Command to roll a dice, optionally for Didier Dinks.
        :param ctx: Discord Context
        :param args: bet & wager
        """
        args = list(args)
        result = random.randint(1, 6)

        # No choice made & no wager
        if len(args) == 0:
            self.updateStats("dice", result)
            return await ctx.send(":game_die: **{}**!".format(result))

        # Check for invalid args
        if len(args) == 1 or not args[0].isdigit() or not 0 < int(args[0]) < 7:
            return await ctx.send("Controleer je argumenten.")

        args[1] = abbreviated(args[1])
        valid = checks.isValidAmount(ctx, args[1])

        # Invalid amount
        if not valid[0]:
            return await ctx.send(valid[1])

        await self.gamble(ctx, args[0], str(result), valid[1], 6, ":game_die: ")
        self.updateStats("dice", result)

    @dice.command(name="Stats", hidden=True)
    async def dice_stats(self, ctx):
        await self.client.get_cog("Stats").callStats("dice", ctx)

    async def gamble(self, ctx, bet, result, wager, factor, pre="", post=""):
        """
        Function for gambling because it's the same thing every time.
        :param ctx: Discord Context
        :param bet: the option the user bet on
        :param result: randomly generated result
        :param wager: size of the bet of the user
        :param factor: the factor by which the person's wager is amplified
        :param pre: any string that might have to be pre-pended to the output string
        :param post: any string that might have to be appended to the output string
        :return: a boolean indicating whether or not the user has won
        """
        # Code no longer first removes your bet to then add profit,
        # resulting in triple coinflip profit (@Clement).
        # Subtract one off of the factor to compensate for the initial wager
        factor -= 1
        answer = "**{}**! ".format(result)
        won = False

        # Check if won
        if result[0].lower() == bet[0].lower():
            won = True
            answer += "Je wint **{:,}** Didier Dink{}"
            currency.update(ctx.author.id, "dinks", float(currency.dinks(ctx.author.id)) + (float(wager) * factor))
        else:
            answer += "Je hebt je inzet (**{:,}** Didier Dink{}) verloren"
            currency.update(ctx.author.id, "dinks", float(currency.dinks(ctx.author.id)) - float(wager))
            self.loseDinks(round(float(wager)))

        # If won -> multiple dinkS, if lost, it's possible that the user only bet on 1 dinK
        await ctx.send(pre + answer.format(round(float(wager) * factor if won else float(wager)),
                                           checks.pluralS(float(wager) * factor if won else float(wager))) +
                       ", **{}**!".format(ctx.author.display_name))
        return won

    @commands.group(name="Slots", usage="[Aantal]", case_insensitive=True, invoke_without_command=True)
    @commands.check(checks.allowedChannels)
    @help.Category(category=Category.Gamble)
    async def slots(self, ctx, wager: Abbreviated = None):
        """
        Command to play slot machines.
        :param ctx: Discord Context
        :param wager: the amount of Didier Dinks to bet with
        """
        valid = checks.isValidAmount(ctx, wager)
        # Invalid amount
        if not valid[0]:
            return await ctx.send(valid[1])

        ratios = dinks.getRatios()

        def randomKey():
            return random.choice(list(ratios.keys()))

        def generateResults():
            return [randomKey(), randomKey(), randomKey()]

        # Generate the result
        result = generateResults()

        textFormatted = "{}\n{}\n:yellow_square:{}:yellow_square:\n:arrow_right:{}:arrow_left::part_alternation_mark:\n" \
                        ":yellow_square:{}:yellow_square:   :red_circle:\n{}\n{}".format(
                         dinks.slotsHeader, dinks.slotsEmptyRow,
                         "".join(generateResults()), "".join(result), "".join(generateResults()),
                         dinks.slotsEmptyRow, dinks.slotsFooter)

        await ctx.send(textFormatted)

        # Everything different -> no profit
        if len(set(result)) == 3:
            await ctx.send("Je hebt je inzet (**{:,}** Didier Dinks) verloren, **{}**.".format(
                math.floor(float(valid[1])), ctx.author.display_name
            ))
            currency.update(ctx.author.id, "dinks", float(currency.dinks(ctx.author.id)) - math.floor(float(valid[1])))
            return

        # Calculate the profit multiplier
        multiplier = 1.0
        for symbol in set(result):
            multiplier *= ratios[symbol][result.count(symbol) - 1]

        await ctx.send(":moneybag: Je wint **{:,}** Didier Dinks, **{}**! :moneybag:".format(
            round(float(valid[1]) * multiplier, 2), ctx.author.display_name
        ))
        currency.update(ctx.author.id, "dinks",
                        float(currency.dinks(ctx.author.id)) + (float(valid[1]) * multiplier) - math.floor(
                            float(valid[1])))
        # Current Dinks - wager + profit

    # Returns list of profits
    @slots.command(name="Chart", aliases=["Symbols", "Profit"])
    async def chart(self, ctx):
        """
        Command to show the profit distributions for the Didier Slotmachines.
        :param ctx: Discord Context
        """
        embed = discord.Embed(colour=discord.Colour.blue())
        embed.set_author(name="Slots Profit Chart")
        ratios = dinks.getRatios()

        # Add every symbol into the embed
        for ratio in ratios:
            embed.add_field(name=ratio, value="1: x{}\n2: x{}\n3: x{}".format(
                str(ratios[ratio][0]), str(ratios[ratio][1]), str(ratios[ratio][2])
            ))

        await ctx.send(embed=embed)

    @commands.group(name="Lost", case_insensitive=True, invoke_without_command=True)
    @commands.check(checks.allowedChannels)
    @help.Category(category=Category.Gamble)
    async def lost(self, ctx):
        """
        Command that shows the amount of Didier Dinks that have been lost due to gambling.
        :param ctx: Discord Context
        """
        await ctx.send("Er zijn al **{:,}** Didier Dinks verloren sinds 13/03/2020."
                       .format(dinks.lost()))

    @lost.command(name="Today")
    async def today(self, ctx):
        """
        Command that shows the amount of Didier Dinks lost today.
        :param ctx: Discord Context
        """
        await ctx.send("Er zijn vandaag al **{:,}** Didier Dinks verloren."
                       .format(dinks.lostToday()))

    def updateStats(self, game, key):
        """
        Function to update the stats file for a game.
        :param game: the game to change the stats for
        :param key: the key in the game's dict to update
        """
        with open("files/stats.json", "r") as fp:
            s = json.load(fp)

        s[game][str(key)] += 1

        with open("files/stats.json", "w") as fp:
            json.dump(s, fp)

    def loseDinks(self, amount):
        """
        Function that adds Didier Dinks to the lost file.
        :param amount: the amount of Didier Dinks lost
        """
        with open("files/lost.json", "r") as fp:
            fc = json.load(fp)
            fc["lost"] = fc["lost"] + round(amount)
            fc["today"] = fc["today"] + round(amount)
        with open("files/lost.json", "w") as fp:
            json.dump(fc, fp)


def setup(client):
    client.add_cog(Games(client))
