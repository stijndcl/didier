from typing import Optional

from discord import app_commands
from discord.ext import commands

from didier import Didier


class Games(commands.Cog):
    """Cog for various games"""

    client: Didier

    def __init__(self, client: Didier):
        self.client = client

    @app_commands.command(name="wordle", description="Play Wordle!")
    async def wordle(self, ctx: commands.Context, guess: Optional[str] = None):
        """View your active Wordle game

        If an argument is provided, make a guess instead
        """


async def setup(client: Didier):
    """Load the cog"""
    await client.add_cog(Games(client))
