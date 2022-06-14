from discord.ext import commands

from didier import Didier


class TestCog(commands.Cog):
    client: Didier

    def __init__(self, client: Didier):
        self.client = client


async def setup(client: Didier):
    await client.add_cog(TestCog(client))
