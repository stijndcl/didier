from data import constants
import discord
from discord.ext import commands
from decorators import help
from enums.help_categories import Category


class Utils(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.client.locked = False
        self.client.lockedUntil = -1

    # Don't allow any commands to work when locked
    def cog_check(self, ctx):
        return not self.client.locked

    # Marco Polo to check if bot is running & delay
    @commands.command(name="Marco")
    @help.Category(category=Category.Didier)
    async def marco(self, ctx):
        await ctx.send("Polo! {}ms".format(round(self.client.latency * 1000)))

    async def removeMessage(self, message):
        try:
            await message.delete()
        except discord.Forbidden:
            pass

    # Send a DM to a user
    async def sendDm(self, userid, message: str):
        user = self.client.get_user(int(userid))
        await user.send(message)

    # Send an Embed to a user
    async def sendEmbed(self, userid, embed):
        await discord.utils.get(self.client.get_all_members(), id=int(userid)).send(embed=embed)

    # Returns a member object of a user
    def getMember(self, ctx, memberid):
        if str(ctx.channel.type) == "private" or ctx.guild.get_member(int(memberid)) is None:
            if str(memberid) == str(ctx.author.id):
                return ctx.author
            COC = self.client.get_guild(int(constants.CallOfCode))
            return COC.get_member(int(memberid))

        return ctx.guild.get_member(int(memberid))

    # Returns a user's display name if he's in this server, else COC
    def getDisplayName(self, ctx, memberid):
        # Checks if this is a DM, or the user is not in the guild
        if str(ctx.channel.type) == "private" or ctx.guild.get_member(int(memberid)) is None:
            if str(memberid) == str(ctx.author.id):
                return ctx.author.display_name
            COC = self.client.get_guild(int(constants.CallOfCode))
            member = COC.get_member(int(memberid))
            if member is not None:
                return member.display_name
            return "[Persoon die de server misschien geleaved is | {}]".format(memberid)

        mem = ctx.guild.get_member(int(memberid))
        return mem.display_name


def setup(client):
    client.add_cog(Utils(client))
