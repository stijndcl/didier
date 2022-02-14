from data import constants
from decorators import help
import discord
from discord.ext import commands
from enums.help_categories import Category
from functions import checks, config, timeFormatters
from functions.database import memes, githubs, twitch, dadjoke
from functions.database.custom_commands import add_command, add_alias
import json
import os


class ModCommands(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.utilsCog = self.client.get_cog('Utils')

    @commands.command(name="Remove", aliases=["Rm"], hidden=True)
    @commands.check(checks.isMe)
    @help.Category(category=Category.Mod)
    async def remove(self, ctx, message: str):
        spl = message.split("/")
        channel = self.client.get_channel(int(spl[-2]))
        message = await channel.fetch_message(int(spl[-1]))
        await message.delete()

    # Load a cog
    @commands.group(name="Load", usage="[Cog]", case_insensitive=True, invoke_without_command=True)
    @commands.check(checks.isMe)
    @help.Category(category=Category.Mod)
    async def load(self, ctx, extension: str):
        try:
            self.client.load_extension("cogs.{}".format(extension))
            await self.sendDm(constants.myId, "Loaded **{}**".format(extension))
        except discord.ExtensionAlreadyLoaded:
            await self.sendDm(constants.myId, "**{}** has already been loaded".format(extension))

    @commands.command(name="Config", aliases=["Setup", "Set"], case_insensitive=True, usage="[Categorie] [Value]",
                      invoke_without_commands=True)
    @commands.check(checks.isMe)
    @help.Category(Category.Mod)
    async def set(self, ctx, category, value):
        if config.config(category, value):
            await ctx.message.add_reaction("✅")

    # Load all cogs except for modCommands
    @load.command(name="All")
    async def loadAll(self, ctx):
        for file in os.listdir("./cogs"):
            if file.endswith(".py") and not file == "modCommands.py":
                await self.load(ctx, file[:-3])

    # Unload a cog
    @commands.group(name="Unload", usage="[Cog]", case_insensitive=True, invoke_without_command=True)
    @commands.check(checks.isMe)
    @help.Category(category=Category.Mod)
    async def unload(self, ctx, extension: str):
        try:
            self.client.unload_extension("cogs.{}".format(extension))
            await self.sendDm(constants.myId, "Unloaded **{}**".format(extension))
        except discord.ExtensionNotLoaded:
            await self.sendDm(constants.myId, "**{}** has already been unloaded".format(extension))

    # Unload all cogs except for modCommands
    @unload.command(name="All")
    async def unloadAll(self, ctx):
        for file in os.listdir("./cogs"):
            if file.endswith(".py") and not file == "modCommands.py":
                await self.unload(ctx, file[:-3])

    # Reloads a cog
    @commands.command(name="Reload", aliases=["Update"], usage="[Cog]")
    @commands.check(checks.isMe)
    @help.Category(category=Category.Mod)
    async def reload(self, ctx, cog):
        await self.unload(ctx, cog)
        await self.load(ctx, cog)
        await ctx.message.add_reaction("✅")

    # Repeat what was said
    @commands.command(name="Repeat", usage="[Text]")
    @commands.check(checks.isMe)
    @help.Category(category=Category.Mod)
    async def repeat(self, ctx, *text):
        await self.utilsCog.removeMessage(ctx.message)
        await ctx.send(" ".join(text))

    # Add a reaction to a message
    @commands.command(name="Reac", aliases=["Reacc"], usage="[Emoji] [Id]")
    @commands.check(checks.isMe)
    @help.Category(category=Category.Mod)
    async def reac(self, ctx, emoji, messageId):
        channel = ctx.channel

        # Check if the URL or the Id was passed
        if messageId.count("/") > 3:
            spl = messageId.split("/")
            channel = self.client.get_channel(int(spl[-2]))
            if channel is None:
                return await ctx.send("Ik kan geen kanaal zien met dit Id.")
            messageId = int(spl[-1])

        await self.utilsCog.removeMessage(ctx.message)
        message = await channel.fetch_message(messageId)
        if message is None:
            return await ctx.send("Ik kan geen bericht zien met dit Id.")
        await message.add_reaction(emoji)

    @commands.group(name="Add", usage="[Category] [Args]", case_insensitive=True, invoke_without_command=False)
    @commands.check(checks.isMe)
    @help.Category(category=Category.Mod)
    async def add(self, ctx):
        """
        Commands group that adds database entries
        """
        pass

    @add.command(name="Custom", usage="[Name] [Response]")
    async def custom(self, ctx, name, *, resp):
        err_msg = add_command(name, resp)

        # Something went wrong
        if err_msg:
            return await ctx.send(err_msg)
        else:
            await ctx.message.add_reaction("✅")

    @add.command(name="Alias", usage="[Name] [Alias]")
    async def add_alias(self, ctx, command, alias):
        err_msg = add_alias(command, alias)

        # Something went wrong
        if err_msg:
            return await ctx.send(err_msg)
        else:
            await ctx.message.add_reaction("✅")

    @add.command(name="Dadjoke", aliases=["Dj", "Dad"], usage="[Joke]")
    async def dadjoke(self, ctx, *, joke):
        dadjoke.addJoke(joke)
        await ctx.send("Added ``{}``.".format(joke))
        await ctx.message.add_reaction("✅")

    @add.command(name="8-Ball", aliases=["8b", "Eightball", "8Ball"], usage="[Response]")
    async def eightball(self, ctx, message):
        with open("files/eightball.json", "r") as fp:
            file = json.load(fp)
        file.append(message)
        with open("files/eightball.json", "w") as fp:
            json.dump(file, fp)

    # Adds a meme into the database
    @add.command(name="Meme", aliases=["Mem"], usage="[Id] [Name] [Aantal Velden]")
    async def meme(self, ctx, memeid, meme, fields):
        await ctx.send(memes.insert(memeid, meme, fields))

    # Adds a person's GitHub into the database
    @add.command(name="GitHub", aliases=["Gh", "Git"], usage="[Id] [Link]")
    async def github(self, ctx, userid, link):
        # Allow tagging to work as well
        if len(ctx.message.mentions) == 1:
            userid = ctx.message.mentions[0].id
        githubs.add(userid, link)
        await ctx.send("{}'s GitHub is toegevoegd aan de database.".format(self.utilsCog.getDisplayName(ctx, userid)))

    # Adds a person's Twitch into the database
    @add.command(name="Twitch", aliases=["Stream", "Streamer", "Tw"])
    async def twitch(self, ctx, userid, link):
        # Allow tagging to work as well
        if len(ctx.message.mentions) == 1:
            userid = ctx.message.mentions[0].id
        twitch.add(userid, link)
        await ctx.send("{}'s Twitch is toegevoegd aan de database.".format(self.utilsCog.getDisplayName(ctx, userid)))

    @commands.command(name="WhoIs", aliases=["Info", "Whodis"], usage="[@User]")
    @help.Category(Category.Mod)
    async def whois(self, ctx, user: discord.User = None):
        if user is None:
            return

        embed = discord.Embed(colour=discord.Colour.blue())

        embed.set_author(name=user.display_name, icon_url=user.avatar.url)
        embed.add_field(name="Discriminator", value=f"#{user.discriminator}")
        embed.add_field(name="Discord id", value=user.id)
        embed.add_field(name="Bot", value="Nee" if not user.bot else "Ja")

        created_local = timeFormatters.epochToDate(user.created_at.timestamp())

        embed.add_field(name="Account aangemaakt", value=f"<t:{round(created_local['dateDT'].timestamp())}:R>", inline=False)

        # Check if the user is in the current guild
        if ctx.guild is not None:
            member_instance = ctx.guild.get_member(user.id)

            if member_instance is not None:
                joined_local = timeFormatters.epochToDate(member_instance.joined_at.timestamp())

                embed.add_field(name=f"Lid geworden van {ctx.guild.name}",
                                value=f"<t:{round(joined_local['dateDT'].timestamp())}:R>")

                embed.add_field(name="Mention String", value=member_instance.mention, inline=False)

        await ctx.send(embed=embed)

    # Send a DM to a user -- Can't re-use Utils cog in (un)load because the cog might not be loaded
    async def sendDm(self, userid, message: str):
        user = self.client.get_user(int(userid))
        await user.send(message)


def setup(client):
    client.add_cog(ModCommands(client))
