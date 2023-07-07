from discord.ext import commands

from didier import Didier


class Games(commands.Cog):
    """Cog for various games"""

    client: Didier

    def __init__(self, client: Didier):
        self.client = client


async def setup(client: Didier):
    """Load the cog"""
    await client.add_cog(Games(client))
