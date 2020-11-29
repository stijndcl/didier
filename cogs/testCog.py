from discord.ext import commands
from functions import checks


class TestCog(commands.Cog):

    def __init__(self, client):
        self.client = client

    # All commands in this Cog should only be accessible to me
    def cog_check(self, ctx):
        return checks.isMe(ctx)

    @commands.command()
    async def test(self, ctx):
        pass

    @test.error
    async def test_handler(self, ctx, error):
        raise error


def setup(client):
    client.add_cog(TestCog(client))
