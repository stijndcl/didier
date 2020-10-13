import discord
from discord.ext import commands
from decorators import help
from enums.help_categories import Category
from functions.database import muttn


class Muttn(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Don't allow any commands to work when locked
    def cog_check(self, ctx):
        return not self.client.locked

    @commands.group(name="Muttn", aliases=["HowMuttn", "M", "Mutn", "Mutten"], usage="[@Persoon]", case_insensitive=True, invoke_without_command=True)
    @help.Category(Category.Fun)
    async def muttn(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        user = muttn.getOrAddUser(member.id)

        embed = discord.Embed(colour=discord.Colour.blue(), title=member.display_name)
        embed.set_author(name="Muttn-O'-Meter")
        embed.add_field(name="Percentage", value="{}%".format(round(float(user[1]), 2)))

        embed.add_field(name="Aantal {}'s".format("<:Muttn:761551956346798111>"), value=str(user[2]))
        await ctx.send(embed=embed)

    @muttn.command(name="Leaderboard", aliases=["Lb"], hidden=True)
    async def lb(self, ctx):
        await self.client.get_cog("Leaderboards").callLeaderboard("muttn", ctx)


def setup(client):
    client.add_cog(Muttn(client))
