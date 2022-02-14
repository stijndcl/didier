from decorators import help
import discord
from discord.ext import commands
from enums.help_categories import Category
from functions import checks
from functions.database import githubs, twitch


class SelfPromo(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.utilsCog = self.client.get_cog("Utils")

    # Don't allow any commands to work when locked
    def cog_check(self, ctx):
        return not self.client.locked

    @commands.group(name="GitHub", aliases=["Git", "GitHubs", "Gh"], case_insensitive=True, usage="[@Persoon]*", invoke_without_command=True)
    @commands.check(checks.allowedChannels)
    @help.Category(category=Category.Other)
    async def github(self, ctx, member: discord.Member = None):
        # Get a specific member's GitHub
        if member:
            user_git = githubs.get_user(member.id)
            if not user_git:
                return await ctx.send("**{}** heeft zijn GitHub link nog niet doorgegeven.".format(member.display_name))

            return await self.createPersonalPromo(ctx, member, user_git[0][0], discord.Colour.from_rgb(250, 250, 250), "GitHub")

        l = githubs.getAll()
        await self.createPromoEmbed(ctx, l, discord.Colour.from_rgb(250, 250, 250), "GitHub", "files/images/github.png")

    @github.command(name="Add", aliases=["Insert", "Register", "Set"], usage="[Link]")
    async def githubadd(self, ctx, link):
        if "github.com" not in link.lower() and "github.ugent.be" not in link.lower() and "gitlab.com" not in link.lower():
            link = "https://github.com/{}".format(link)

        githubs.add(ctx.author.id, link)
        await ctx.message.add_reaction("✅")

    @commands.group(name="Twitch", aliases=["Streams"], case_insensitive=True, usage="[@Persoon]", invoke_without_command=True)
    @commands.check(checks.allowedChannels)
    @help.Category(category=Category.Other)
    async def twitch(self, ctx, member: discord.Member = None):
        # Get a specific member's GitHub
        if member:
            user_twitch = twitch.get_user(member.id)
            if not user_twitch:
                return await ctx.send("**{}** heeft zijn Twitch link nog niet doorgegeven.".format(member.display_name))

            return await self.createPersonalPromo(ctx, member, user_twitch[0][0], discord.Colour.from_rgb(100, 65, 165), "Twitch")

        l = twitch.getAll()
        await self.createPromoEmbed(ctx, l, discord.Colour.from_rgb(100, 65, 165), "Twitch", "files/images/twitch.png")

    @twitch.command(name="Add", aliases=["Insert", "Register", "Set"], usage="[Link]")
    async def twitchadd(self, ctx, link):
        if "twitch.tv" not in link.lower():
            link = "https://www.twitch.tv/{}".format(link)

        twitch.add(ctx.author.id, link)
        await ctx.message.add_reaction("✅")

    # Creates embed with everyone's links & a fancy image
    async def createPromoEmbed(self, ctx, users, colour, type, imageUrl=None):
        # Image file
        file = None

        # Sort users by Discord name
        users = [[self.utilsCog.getMember(ctx, user[0]), user[1]] for user in users if self.utilsCog.getMember(ctx, user[0]) is not None]
        users.sort(key=lambda x: x[0].name)

        embed = discord.Embed(colour=colour)
        if imageUrl is not None:
            # Link
            if "https" in imageUrl:
                embed.set_thumbnail(url=imageUrl)
            else:
                # Local file
                file = discord.File(imageUrl, filename="icon.png")
                embed.set_thumbnail(url="attachment://icon.png")
        embed.set_author(name="{} Links".format(type))
        for user in users:
            embed.add_field(name="{} ({})".format(
                user[0].display_name, user[0].name
            ), value=user[1], inline=False)
        embed.set_footer(text="Wil je je eigen {0} hierin? Gebruik {0} Add [Link] of stuur een DM naar DJ STIJN.".format(type))
        if file is not None:
            await ctx.send(embed=embed, file=file)
        else:
            await ctx.send(embed=embed)

    async def createPersonalPromo(self, ctx, user, link, colour, type):
        embed = discord.Embed(colour=colour)
        embed.set_author(name="{} Links".format(type), icon_url=user.avatar.url)
        embed.add_field(name="{} link van {}".format(type, user.display_name), value=link)
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(SelfPromo(client))
