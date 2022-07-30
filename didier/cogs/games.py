from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from database.constants import WORDLE_GUESS_COUNT, WORDLE_WORD_LENGTH
from database.crud.wordle import (
    get_active_wordle_game,
    make_wordle_guess,
    start_new_wordle_game,
)
from didier import Didier
from didier.data.embeds.wordle import WordleEmbed, WordleErrorEmbed


class Games(commands.Cog):
    """Cog for various games"""

    client: Didier

    def __init__(self, client: Didier):
        self.client = client

    @app_commands.command(name="wordle", description="Play Wordle!")
    async def wordle(self, interaction: discord.Interaction, guess: Optional[str] = None):
        """View your active Wordle game

        If an argument is provided, make a guess instead
        """
        await interaction.response.defer(ephemeral=True)

        # Guess is wrong length
        if guess is not None and len(guess) != 0 and len(guess) != WORDLE_WORD_LENGTH:
            embed = WordleErrorEmbed(message=f"Guess must be 5 characters, but `{guess}` is {len(guess)}.").to_embed()
            return await interaction.followup.send(embed=embed)

        active_game = await get_active_wordle_game(self.client.mongo_db, interaction.user.id)
        if active_game is None:
            active_game = await start_new_wordle_game(self.client.mongo_db, interaction.user.id)

        # Trying to guess with a complete game
        if len(active_game.guesses) == WORDLE_GUESS_COUNT and guess:
            embed = WordleErrorEmbed(message="You've already completed today's Wordle.\nTry again tomorrow!").to_embed()
            return await interaction.followup.send(embed=embed)

        # Make a guess
        if guess:
            # The guess is not a real word
            if guess.lower() not in self.client.wordle_words:
                embed = WordleErrorEmbed(message=f"`{guess}` is not a valid word.").to_embed()
                return await interaction.followup.send(embed=embed)

            guess = guess.lower()
            await make_wordle_guess(self.client.mongo_db, interaction.user.id, guess)

            # Don't re-request the game, we already have it
            # just append locally
            active_game.guesses.append(guess)

        embed = WordleEmbed(game=active_game, word=self.client.database_caches.wordle_word.data[0]).to_embed()
        await interaction.followup.send(embed=embed)


async def setup(client: Didier):
    """Load the cog"""
    await client.add_cog(Games(client))
