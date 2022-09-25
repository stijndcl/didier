from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from database.constants import WORDLE_WORD_LENGTH
from database.crud.wordle import get_wordle_guesses, make_wordle_guess
from database.crud.wordle_stats import complete_wordle_game
from didier import Didier
from didier.data.embeds.wordle import WordleEmbed, WordleErrorEmbed, is_wordle_game_over


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

        word_instance = self.client.database_caches.wordle_word.word

        async with self.client.postgres_session as session:
            guesses = await get_wordle_guesses(session, interaction.user.id)

            # Trying to guess with a complete game
            if is_wordle_game_over(guesses, word_instance.word):
                embed = WordleErrorEmbed(
                    message="You've already completed today's Wordle.\nTry again tomorrow!"
                ).to_embed()
                return await interaction.followup.send(embed=embed)

            # Make a guess
            if guess:
                # The guess is not a real word
                if guess.lower() not in self.client.wordle_words:
                    embed = WordleErrorEmbed(message=f"`{guess}` is not a valid word.").to_embed()
                    return await interaction.followup.send(embed=embed)

                guess = guess.lower()
                await make_wordle_guess(session, interaction.user.id, guess)

                # Don't re-request the game, we already have it
                # just append locally
                guesses.append(guess)

            embed = WordleEmbed(guesses=guesses, word=word_instance).to_embed()
            await interaction.followup.send(embed=embed)

            # After responding to the interaction: update stats in the background
            game_over = is_wordle_game_over(guesses, word_instance.word)
            if game_over:
                await complete_wordle_game(session, interaction.user.id, word_instance.word in guesses)


async def setup(client: Didier):
    """Load the cog"""
    await client.add_cog(Games(client))
