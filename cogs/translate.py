from decorators import help
import discord
from discord.ext import commands
from enums.help_categories import Category
from functions.stringFormatters import title_case as tc
from googletrans import Translator, LANGUAGES
import re


class Translate(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Don't allow any commands to work when locked
    def cog_check(self, ctx):
        return not self.client.locked

    @commands.command(name="Translate", aliases=["Tl", "Trans"], usage="[Tekst] [Van]* [Naar]*")
    @help.Category(Category.Words)
    async def translate(self, ctx, query=None, to="nl", fr="auto"):
        if query is None:
            return await ctx.send("Controleer je argumenten.")

        success, query = await self.getQuery(ctx, query)
        if not success:
            return await ctx.send(query)

        translator = Translator()

        # From & To were provided, swap them
        if fr != "auto":
            temp = fr
            fr = to
            to = temp

        try:
            translation = translator.translate(query, to, fr)
            embed = discord.Embed(colour=discord.Colour.blue())
            embed.set_author(name="Didier Translate")

            if fr == "auto":
                language = translation.src
                embed.add_field(name="Gedetecteerde taal", value=tc(LANGUAGES[language]))

                if translation.extra_data["confidence"] is not None:
                    embed.add_field(name="Zekerheid", value="{}%".format(translation.extra_data["confidence"] * 100))

            embed.add_field(name="Origineel ({})".format(translation.src.upper()), value=query, inline=False)
            embed.add_field(name="Vertaling ({})".format(to.upper()), value=translation.text)

            await ctx.send(embed=embed)
        except ValueError as e:
            message = str(e)
            if "destination" in message:
                return await ctx.send("{} is geen geldige taal.".format(tc(to)))

            if "source" in message:
                return await ctx.send("{} is geen geldige taal.".format(tc(fr)))

            raise e

    # @commands.command(name="Detect", aliases=["Ld"], usage="[Tekst]")
    # @help.Category(Category.Words)
    async def detect(self, ctx, query=None):
        if query is None:
            return await ctx.send("Controleer je argumenten.")

        success, query = await self.getQuery(ctx, query)
        if not success:
            return await ctx.send(query)

        translator = Translator()
        language = translator.detect(query)

        confidence = language.confidence * 100

        embed = discord.Embed(colour=discord.Colour.blue())
        embed.set_author(name="Language Detection")
        embed.add_field(name="Zin", value=query, inline=False)
        embed.add_field(name="Gedetecteerde taal", value=tc(LANGUAGES[language.lang]))
        embed.add_field(name="Zekerheid", value="{}%".format(confidence))
        await ctx.send(embed=embed)

    async def getQuery(self, ctx, query):
        # Check if it's a link to a message
        if re.match(r"^https://discord.com/channels/[0-9A-Za-z@]+/[0-9]+/[0-9]+$", query):
            spl = query.split("/")
            channel = self.client.get_channel(int(spl[-2]))
            if channel is None:
                return False, "Ik kan geen kanaal zien met dit id."

            message = await channel.fetch_message(spl[-1])
            if message is None:
                return False, "Ik kan geen bericht zien met dit id."

            query = message.content

        else:
            try:
                # An id was passed instead
                query = int(query)
                message = await ctx.channel.fetch_message(query)
                if message is None:
                    return False, "Ik kan geen bericht zien met dit id."
                query = message.content
            except ValueError:
                pass

        if not query:
            return False, "Dit is geen geldig bericht."

        return True, query


def setup(client):
    client.add_cog(Translate(client))
