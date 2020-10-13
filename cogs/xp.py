from data import constants
from decorators import help
import discord
from discord.ext import commands
from enums.help_categories import Category
from functions import checks, xp
from functions.database import stats


class Xp(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.group(name="Xp", aliases=["Level", "Mc", "Mess", "Messages"], case_insensitive=True, invoke_without_command=True)
    @commands.check(checks.allowedChannels)
    @help.Category(Category.Other)
    async def xp(self, ctx, user: discord.Member = None):
        if user is not None and str(ctx.author.id) != constants.myId:
            return await ctx.send("Je hebt geen toegang tot dit commando.")

        target = user if user is not None else ctx.author

        target_stats = stats.getOrAddUser(target.id)

        embed = discord.Embed(colour=discord.Colour.blue())
        embed.set_author(name=target.display_name, icon_url=target.avatar_url)
        embed.add_field(name="Aantal Berichten", value="{}".format(int(target_stats[11])))
        embed.add_field(name="Level", value=str(xp.calculate_level(target_stats[12])))
        embed.add_field(name="XP", value="{:,}".format(int(target_stats[12])))
        embed.set_footer(text="*Sinds Didier 2.0 Launch")
        await ctx.send(embed=embed)

    @xp.command(name="Leaderboard", aliases=["Lb"], hidden=True)
    async def xpleaderboard(self, ctx, *args):
        if any(alias in ctx.message.content for alias in ["mc", "mess", "messages"]):
            return await self.client.get_cog("Leaderboards").callLeaderboard("Messages", ctx)
        await self.client.get_cog("Leaderboards").callLeaderboard("Xp", ctx)


def setup(client):
    client.add_cog(Xp(client))
