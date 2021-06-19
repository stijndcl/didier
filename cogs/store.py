from converters.numbers import Abbreviated
from data.menus import storePages
from decorators import help
import discord
from discord.ext import commands
from enums.help_categories import Category
from enums.numbers import Numbers
from functions import checks
from functions.database import store, currency
from functions.numbers import getRep


class Store(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Don't allow any commands to work when locked
    def cog_check(self, ctx):
        return not self.client.locked

    @commands.group(name="Store", aliases=["Shop"], case_insensitive=True, invoke_without_command=True)
    @commands.check(checks.allowedChannels)
    @help.Category(Category.Currency)
    async def store(self, ctx):
        entries = store.getAllItems()
        await storePages.Pages(source=storePages.Source(entries), clear_reactions_after=True).start(ctx)

    @store.command(name="Buy", aliases=["Get"], hidden=True)
    async def storeBuy(self, ctx, item, amount: Abbreviated = 1):
        if amount is None:
            return

        await self.buy(ctx, item, amount)

    @commands.command(name="Buy", aliases=["Get"], usage="[Item id] [Aantal]*")
    @commands.check(checks.allowedChannels)
    @help.Category(Category.Currency)
    async def buy(self, ctx, item, amount: Abbreviated = 1):
        if amount is None:
            return

        try:
            item = int(item)
        except ValueError:
            return await ctx.send("Dit is geen geldig id.")

        success, message = store.buy(ctx, ctx.author.id, item, amount)
        if not success:
            return await ctx.send(message)

        rep = getRep(message["price"], Numbers.t.value)

        return await ctx.send("**{}** heeft **{} {}{}** gekocht voor **{}** Didier Dink{}.".format(
            ctx.author.display_name, amount, message["name"], checks.pluralS(amount),
            rep, checks.pluralS(message["price"])
        ))

    @store.command(name="Sell", hidden=True)
    async def storeSell(self, ctx, itemid, amount: Abbreviated = 1):
        if amount is None:
            return
        await self.sell(ctx, itemid, amount)

    @commands.command(name="Sell", usage="[Item id] [Aantal]")
    @commands.check(checks.allowedChannels)
    @help.Category(Category.Currency)
    async def sell(self, ctx, itemid, amount: Abbreviated = 1):
        if amount is None:
            return

        try:
            itemid = int(itemid)
        except ValueError:
            return await ctx.send("Dit is geen geldig id.")

        inv = store.inventory(ctx.author.id)

        if not inv or not any(int(item[0]) == itemid for item in inv):
            return await ctx.send("Je hebt geen item met dit id.")

        item_tuple = None
        for item in inv:
            if item[0] == itemid:
                item_tuple = item
                break

        if str(amount).lower() == "all":
            amount = int(item_tuple[2])

        if int(item_tuple[2]) < amount:
            return await ctx.send("Je hebt niet zoveel {}s.".format(item_tuple[1]))

        store.sell(int(ctx.author.id), itemid, int(amount), int(item_tuple[2]))
        price = int(store.getItemPrice(itemid)[0])
        returnValue = round(0.8 * (price * amount))

        currency.update(ctx.author.id, "dinks", currency.dinks(ctx.author.id) + returnValue)

        await ctx.send("**{}** heeft **{} {}{}** verkocht voor **{}** Didier Dinks!".format(
            ctx.author.display_name, amount, item_tuple[1], "s" if amount != 1 else "",
            getRep(returnValue, Numbers.t.value)
        ))

    @commands.command(name="Inventory", aliases=["Inv", "Items"])
    @commands.check(checks.allowedChannels)
    @help.Category(Category.Currency)
    async def inventory(self, ctx, *args):
        inv = store.inventory(ctx.author.id)
        inv = sorted(inv, key=lambda x: x[1])
        embed = discord.Embed(colour=discord.Colour.blue())
        embed.set_author(name="Inventory van {}".format(ctx.author.display_name))
        embed.set_thumbnail(url=str(ctx.author.avatar_url))
        if len(inv) == 0:
            embed.description = "Je hebt nog niets gekocht!\n" \
                                "Koop iets in de Store wanneer DJ STIJN niet langer te lui is om er iets in te steken."
        else:
            embed.description = "\n".join("#{} {}: {}".format(item[0], item[1], item[2]) for item in inv)

        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Store(client))
