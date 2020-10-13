import os

from decorators import help
import discord
from discord.ext import commands
from enums.help_categories import Category
from functions import checks
import requests


class Define(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Don't allow any commands to work when locked
    def cog_check(self, ctx):
        return not self.client.locked

    @commands.command(name="Define", aliases=["UrbanDictionary", "Ud"], usage="[Woord]")
    @commands.check(checks.allowedChannels)
    @help.Category(category=Category.Other)
    async def define(self, ctx, *words):
        """
        Command that looks up the definition of a word in the Urban Dictionary.
        :param ctx: Discord Context
        :param words: Word(s) to look up
        """
        words = list(words)
        if len(words) == 0:
            return await ctx.send("Controleer je argumenten.")

        query = " ".join(words)
        answer = self.lookup(query)

        embed = discord.Embed(colour=discord.Colour.from_rgb(220, 255, 0))
        embed.set_author(name="Urban Dictionary")

        embed.add_field(name="Woord", value=answer["word"], inline=True)
        embed.add_field(name="Auteur", value=answer["author"], inline=True)
        embed.add_field(name="Definitie", value=self.cleanString(answer["definition"]), inline=False)
        embed.add_field(name="Voorbeeld", value=self.cleanString(answer["example"]), inline=False)
        embed.add_field(name="Rating", value=str(round(self.ratio(answer), 2)) + "%")
        embed.add_field(name="Link naar de volledige definitie",
                        value="[Urban Dictionary]({})".format(str(answer["link"])))

        await ctx.send(embed=embed)

    def lookup(self, word):
        """
        Function that sends the API request to get the definition.
        :param word: the woord to look up
        :return: a dictionary representing the info of this word
        """
        url = "https://mashape-community-urban-dictionary.p.rapidapi.com/define"

        querystring = {"term": word}

        headers = {
            'x-rapidapi-host': "mashape-community-urban-dictionary.p.rapidapi.com",
            'x-rapidapi-key': os.getenv("URBANDICTIONARY")
        }

        try:
            if word.lower() == "didier":
                raise Exception

            response = requests.request("GET", url, headers=headers, params=querystring).json()["list"]

            if len(response) > 0:
                return {"word": response[0]["word"], "definition": response[0]["definition"],
                        "example": response[0]["example"], "thumbs_up": response[0]["thumbs_up"],
                        "thumbs_down": response[0]["thumbs_down"], "link": response[0]["permalink"],
                        "author": response[0]["author"]}

            # No valid response
            return self.defineDidier()
        except Exception:
            return self.defineDidier()

    def cleanString(self, text: str):
        """
        Function that cuts off definitions that are too long & strips out UD markdown
        from an input string.
        :param text: the input string to clean up
        :return: the edited version of the string
        """
        text = text.replace("[", "")
        text = text.replace("]", "")
        return text if len(text) < 1024 else text[:1021] + "..."

    def ratio(self, dic):
        """
        Function that alculates the upvote/downvote ratio of the definition.
        :param dic: the dictionary representing the definition
        :return: the upvote/downvote ratio (float)
        """
        return (100 * int(dic["thumbs_up"])) / (int(dic["thumbs_up"]) + int(dic["thumbs_down"])) \
            if int(dic["thumbs_down"]) != 0 else 100.0

    def defineDidier(self):
        """
        Function that returns a stock dictionary to define Didier
        in case people call it, or no definition was found.
        :return: a dictionary that defines Didier
        """
        return {"word": "Didier", "definition": "Didier", "example": "1: Didier\n2: Hmm?", "thumbs_up": 69420,
                "thumbs_down": 0, "author": "Didier",
                "link": "https://upload.wikimedia.org/wikipedia/commons/a/a5"
                        "/Didier_Reynders_in_Iranian_Parliament_02.jpg"}


def setup(client):
    client.add_cog(Define(client))
