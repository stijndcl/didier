from decorators import help
import discord
from discord.ext import commands
from enums.help_categories import Category
from functions import reactWord


class ReactWord(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.utilsCog = self.client.get_cog("Utils")

    # Don't allow any commands to work when locked
    def cog_check(self, ctx):
        return not self.client.locked

    @commands.command(name="React", usage="[Tekst] [Message id/url]*")
    @help.Category(category=Category.Other)
    async def react(self, ctx, *words):
        words = list(words)
        message = ctx.message
        target = False

        # Message id or URL passed as final argument
        if (len(words[-1]) == 18 and all(i.isdigit() for i in words[-1])) or "discord.com/channels/" in words[-1]:
            target = True
            message = await commands.MessageConverter().convert(ctx, words[-1])

            # Cut id or URL
            words = words[:-1]

        # Reactions that were added before this command was executed
        previousReactions = ([x.emoji for x in message.reactions]) if len(message.reactions) != 0 else []
        eligible, arr = reactWord.check(list(words), previousReactions)

        if not eligible:
            await ctx.send(arr[0])
        else:
            if target:
                await self.utilsCog.removeMessage(ctx.message)
            for reac in arr:
                await message.add_reaction(reac)

    @commands.command(name="Character", aliases=["Char"], usage="[Karakter]")
    @help.Category(category=Category.Other)
    async def char(self, ctx, char: str = None):
        # Nothing passed
        if char is None:
            return await ctx.send("Controleer je argumenten")

        char = char.lower()

        # Not 1 char passed
        if len(char) != 1 or char not in reactWord.allowedCharacters():
            return await ctx.send("Dit is geen geldig karakter.")

        var = reactWord.getAllVariants(char)

        return await ctx.send("**Karakter**: {}\nOpties (**{}**): {}".format(
            char, len(var), " ".join(var)
        ))


def setup(client):
    client.add_cog(ReactWord(client))
