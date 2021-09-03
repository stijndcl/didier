import discord
from googletrans import Translator, LANGUAGES
from functions.stringFormatters import title_case
from typing import Optional


class Translation:
    def __init__(self, text: str, to: str):
        self.text = text
        self.to = to
        self.embed: Optional[discord.Embed] = None
        self.translation = None

        self.translate(text, to)

    def translate(self, query: str, to: str):
        """
        Translate [query] into [to]
        """
        try:
            translator = Translator()
            self.translation = translator.translate(query, to, "auto")
        except ValueError as e:
            message = str(e)

            if "destination" in message:
                self._create_error_embed(f"{title_case(to)} is geen geldige taal.")

            raise e

    def _create_error_embed(self, message):
        embed = discord.Embed(colour=discord.Colour.red())
        embed.set_author(name="Didier Translate")
        embed.description = message
        self.embed = embed

    def to_embed(self) -> discord.Embed:
        # There's an error embed to show
        if self.embed is not None:
            return self.embed

        embed = discord.Embed(colour=discord.Colour.blue())
        embed.set_author(name="Didier Translate")

        language = self.translation.src
        embed.add_field(name="Gedetecteerde taal", value=title_case(LANGUAGES[language]))

        if self.translation.extra_data["confidence"] is not None:
            embed.add_field(name="Zekerheid", value="{}%".format(self.translation.extra_data["confidence"] * 100))

        embed.add_field(name="Origineel ({})".format(self.translation.src.upper()), value=self.text, inline=False)
        embed.add_field(name="Vertaling ({})".format(self.to.upper()), value=self.translation.text)

        return embed
