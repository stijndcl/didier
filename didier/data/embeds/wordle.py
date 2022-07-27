import enum
from dataclasses import dataclass
from typing import Optional

import discord
from overrides import overrides

from database.constants import WORDLE_GUESS_COUNT, WORDLE_WORD_LENGTH
from database.schemas.mongo import WordleGame
from didier.data.embeds.base import EmbedBaseModel
from didier.utils.types.datetime import int_to_weekday, tz_aware_now

__all__ = ["WordleEmbed", "WordleErrorEmbed"]


def footer() -> str:
    """Create the footer to put on the embed"""
    today = tz_aware_now()
    return f"{int_to_weekday(today.weekday())} {today.strftime('%d/%m/%Y')}"


class WordleColour(enum.IntEnum):
    """Colours for the Wordle embed"""

    EMPTY = 0
    WRONG_LETTER = 1
    WRONG_POSITION = 2
    CORRECT = 3


@dataclass
class WordleEmbed(EmbedBaseModel):
    """Embed for a Wordle game"""

    game: Optional[WordleGame]
    word: str

    def _letter_colour(self, guess: str, index: int) -> WordleColour:
        """Get the colour for a guess at a given position"""
        if guess[index] == self.word[index]:
            return WordleColour.CORRECT

        wrong_letter = 0
        wrong_position = 0

        for i, letter in enumerate(self.word):
            if letter == guess[index] and guess[i] != guess[index]:
                wrong_letter += 1

            if i <= index and guess[i] == guess[index] and letter != guess[index]:
                wrong_position += 1

            if i >= index:
                if wrong_position == 0:
                    break

                if wrong_position <= wrong_letter:
                    return WordleColour.WRONG_POSITION

        return WordleColour.WRONG_LETTER

    def _guess_colours(self, guess: str) -> list[WordleColour]:
        """Create the colour codes for a specific guess"""
        return [self._letter_colour(guess, i) for i in range(WORDLE_WORD_LENGTH)]

    def colour_code_game(self) -> list[list[WordleColour]]:
        """Create the colour codes for an entire game"""
        colours = []

        # Add all the guesses
        if self.game is not None:
            for guess in self.game.guesses:
                colours.append(self._guess_colours(guess))

        # Fill the rest with empty spots
        for _ in range(WORDLE_GUESS_COUNT - len(colours)):
            colours.append([WordleColour.EMPTY] * WORDLE_WORD_LENGTH)

        return colours

    def _colours_to_emojis(self, colours: list[list[WordleColour]]) -> list[list[str]]:
        """Turn the colours of the board into Discord emojis"""
        colour_map = {
            WordleColour.EMPTY: ":white_large_square:",
            WordleColour.WRONG_LETTER: ":black_large_square:",
            WordleColour.WRONG_POSITION: ":orange_square:",
            WordleColour.CORRECT: ":green_square:",
        }

        emojis = []
        for row in colours:
            emojis.append(list(map(lambda char: colour_map[char], row)))

        return emojis

    @overrides
    def to_embed(self) -> discord.Embed:
        colours = self.colour_code_game()

        embed = discord.Embed(colour=discord.Colour.blue(), title="Wordle")
        emojis = self._colours_to_emojis(colours)

        rows = [" ".join(row) for row in emojis]

        for i, guess in enumerate(self.game.guesses):
            rows[i] += f"   ||{guess.upper()}||"

        embed.description = "\n\n".join(rows)

        # If the game is over, reveal the word
        if len(self.game.guesses) == WORDLE_GUESS_COUNT or (self.game.guesses and self.game.guesses[-1] == self.word):
            embed.description += f"\n\nThe word was **{self.word.upper()}**!"

        embed.set_footer(text=footer())

        return embed


@dataclass
class WordleErrorEmbed(EmbedBaseModel):
    """Embed to send error messages to the user"""

    message: str

    @overrides
    def to_embed(self) -> discord.Embed:
        embed = discord.Embed(colour=discord.Colour.red(), title="Wordle")
        embed.description = self.message
        embed.set_footer(text=footer())
        return embed
