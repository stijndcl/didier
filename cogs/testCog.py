from discord.ext import commands
from functions import checks


class TestCog(commands.Cog):

    def __init__(self, client):
        self.client = client

    def cog_check(self, ctx):
        """
        Check executed for every command in this cog.

        If necessary, create your own check here. A check is just a function
        that returns True or False, and takes ctx as an argument. A command will
        only be executed when this check returns True, which is why that is the default
        implementation for this function.
        """
        return True

    @commands.command()
    async def test(self, ctx):
        pass

    @test.error
    async def test_handler(self, ctx, error):
        raise error


def setup(client):
    client.add_cog(TestCog(client))
