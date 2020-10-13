from converters.numbers import Abbreviated
from decorators import help
import discord
from discord.ext import commands
from enums.help_categories import Category
from functions import checks, timeFormatters
from functions.database import currency
import requests


class Bitcoin(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Don't allow any commands to work when locked
    def cog_check(self, ctx):
        return not self.client.locked

    @commands.group(name="Bitcoin", aliases=["Bc"], case_insensitive=True, invoke_without_command=True)
    @commands.check(checks.allowedChannels)
    @help.Category(category=Category.Currency)
    async def bc(self, ctx):
        """
        Command that shows your Bitcoin bank.
        :param ctx: Discord Context
        """
        price = self.getPrice()
        bc = float(currency.getOrAddUser(ctx.author.id)[8])

        currentTime = timeFormatters.dateTimeNow()
        currentTimeFormatted = currentTime.strftime('%m/%d/%Y om %H:%M:%S')

        # Create the embed
        embed = discord.Embed(colour=discord.Colour.gold())
        embed.set_author(name="Bitcoin Bank van {}".format(ctx.author.display_name))
        embed.add_field(name="Aantal Bitcoins:", value="{:,}".format(round(bc, 8)), inline=False)
        embed.add_field(name="Huidige waarde:", value="{:,} Didier Dink{}"
                        .format(round(bc * price, 8), checks.pluralS(bc * price)), inline=False)
        embed.set_footer(text="Huidige Bitcoin prijs: €{:,} ({})".format(price, str(currentTimeFormatted)))

        # Add the Bitcoin icon to the embed
        file = discord.File("files/images/bitcoin.png", filename="icon.png")
        embed.set_thumbnail(url="attachment://icon.png")

        await ctx.send(embed=embed, file=file)

    @bc.command(name="Price")
    async def price(self, ctx):
        """
        Command that shows the current Bitcoin price.
        :param ctx: Discord Context
        """
        price = self.getPrice()
        currentTime = timeFormatters.dateTimeNow()
        currentTimeFormatted = currentTime.strftime('%m/%d/%Y om %H:%M:%S')
        await ctx.send(
            "Huidige Bitcoin prijs: **€{:,}** ({}).".format(price, str(currentTimeFormatted)))

    @bc.command(name="Buy", usage="[Aantal]")
    async def buy(self, ctx, amount: Abbreviated):
        """
        Command to buy Bitcoins.
        :param ctx: Discord Context
        :param amount: the amount of Bitcoins the user wants to buy
        """

        resp = checks.isValidAmount(ctx, amount)

        # Not a valid amount: send the appropriate error message
        if not resp[0]:
            return await ctx.send(resp[1])

        if amount == "all":
            amount = resp[1]

        # Calculate the amount of Bitcoins the user can buy with [amount] of Didier Dinks
        price = self.getPrice()
        purchased = round(float(amount) / price, 8)

        # Update the db
        currency.update(ctx.author.id, "dinks", float(currency.dinks(ctx.author.id)) - float(amount))
        currency.update(ctx.author.id, "bitcoins",
                        float(currency.getOrAddUser(ctx.author.id)[8]) + float(purchased))

        await ctx.send("**{}** heeft **{:,}** Bitcoin{} gekocht voor **{:,}** Didier Dink{}!"
                       .format(ctx.author.display_name, purchased, checks.pluralS(purchased),
                               round(float(amount)), checks.pluralS(amount)))

    @bc.command(name="Sell", usage="[Aantal]")
    async def sell(self, ctx, amount: Abbreviated):
        """
        Command to sell Bitcoins.
        :param ctx: Discord Context
        :param amount: the amount of Bitcoins the user wants to sell
        """
        if amount == "all":
            amount = float(currency.getOrAddUser(ctx.author.id)[8])

        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError

            bc = float(currency.getOrAddUser(ctx.author.id)[8])

            if bc == 0.0:
                # User has no Bitcoins
                await ctx.send("Je hebt geen Bitcoins, **{}**".format(ctx.author.display_name))
            elif amount > bc:
                # User is trying to sell more Bitcoins that he has
                await ctx.send("Je hebt niet genoeg Bitcoins om dit te doen, **{}**"
                               .format(ctx.author.display_name))
            else:
                price = self.getPrice()
                dinks = float(currency.dinks(ctx.author.id))

                currency.update(ctx.author.id, "bitcoins", bc - amount)
                currency.update(ctx.author.id, "dinks", dinks + (price * amount))

                await ctx.send("**{}** heeft **{:,}** Bitcoin{} verkocht voor **{:,}** Didier Dink{}!"
                               .format(ctx.author.display_name, round(amount, 8), checks.pluralS(amount),
                                       round((price * amount), 8), checks.pluralS(price * amount)))
        except ValueError:
            # Can't be parsed to float -> random string OR smaller than 0
            await ctx.send("Geef een geldig bedrag op.")

    @bc.command(aliases=["Lb", "Leaderboards"], hidden=True)
    @help.Category(category=Category.Other)
    async def leaderboard(self, ctx):
        """
        Command that shows the Bitcoin Leaderboard.
        Alias for Lb Bc.
        :param ctx: Discord Context
        """
        # Call the appropriate leaderboard function
        await self.client.get_cog("Leaderboards").callLeaderboard("bitcoin", ctx)

    def getPrice(self):
        """
        Function to get the current Bitcoin price.
        :return: the current Bitcoin price (float)
        """
        result = requests.get("https://api.coindesk.com/v1/bpi/currentprice.json").json()
        currentPrice = result["bpi"]["EUR"]["rate_float"]
        return float(currentPrice)


def setup(client):
    client.add_cog(Bitcoin(client))
