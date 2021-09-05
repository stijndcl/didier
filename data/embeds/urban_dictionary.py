import discord
import os
import requests
from typing import Dict


class Definition:
    def __init__(self, query: str):
        self.query = query
        self.definition = Definition.lookup(query)

    @staticmethod
    def lookup(word) -> Dict:
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
                return Definition.define_didier()

            response = requests.get(url, headers=headers, params=querystring).json()["list"]

            if len(response) > 0:
                return {"word": response[0]["word"], "definition": response[0]["definition"],
                        "example": response[0]["example"], "thumbs_up": response[0]["thumbs_up"],
                        "thumbs_down": response[0]["thumbs_down"], "link": response[0]["permalink"],
                        "author": response[0]["author"]}

            # No valid response
            return {}
        except Exception:
            return Definition.define_didier()

    @staticmethod
    def clean_string(text: str):
        """
        Function that cuts off definitions that are too long & strips out UD markdown
        from an input string.
        :param text: the input string to clean up
        :return: the edited version of the string
        """
        text = text.replace("[", "")
        text = text.replace("]", "")

        if not text:
            return "N/A"

        return text if len(text) < 1024 else text[:1021] + "..."

    @staticmethod
    def ratio(dic) -> float:
        """
        Function that calculates the upvote/downvote ratio of the definition.
        :param dic: the dictionary representing the definition
        :return: the upvote/downvote ratio (float)
        """
        return (100 * int(dic["thumbs_up"])) / (int(dic["thumbs_up"]) + int(dic["thumbs_down"])) \
            if int(dic["thumbs_down"]) != 0 else 100.0

    @staticmethod
    def define_didier() -> Dict:
        """
        Function that returns a stock dictionary to define Didier
        in case people call it, or no definition was found.
        :return: a dictionary that defines Didier
        """
        return {"word": "Didier", "definition": "Didier", "example": "1: Didier\n2: Hmm?", "thumbs_up": 69420,
                "thumbs_down": 0, "author": "Didier",
                "link": "https://upload.wikimedia.org/wikipedia/commons/a/a5"
                        "/Didier_Reynders_in_Iranian_Parliament_02.jpg"}

    def to_embed(self) -> discord.Embed:
        """
        Create an embed for this definition
        """
        # No results found
        if not self.definition:
            return self._nothing_found_embed()

        embed = discord.Embed(colour=discord.Colour.from_rgb(220, 255, 0))
        embed.set_author(name="Urban Dictionary")

        embed.add_field(name="Woord", value=self.definition["word"], inline=True)
        embed.add_field(name="Auteur", value=self.definition["author"], inline=True)
        embed.add_field(name="Definitie", value=Definition.clean_string(self.definition["definition"]), inline=False)
        embed.add_field(name="Voorbeeld", value=Definition.clean_string(self.definition["example"]), inline=False)
        embed.add_field(name="Rating", value=str(round(Definition.ratio(self.definition), 2)) + "%")
        embed.add_field(name="Link naar de volledige definitie",
                        value="[Urban Dictionary]({})".format(str(self.definition["link"])))

        return embed

    def _nothing_found_embed(self) -> discord.Embed:
        """
        Special embed when no results could be found
        """
        embed = discord.Embed(colour=discord.Colour.red(), title=self.query[:256])
        embed.set_author(name="Urban Dictionary")
        embed.description = "Geen resultaten gevonden"

        return embed
