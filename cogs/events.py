from data import constants
import datetime
import discord
from discord.ext import commands
from functions import checks, easterEggResponses
from functions.database import stats, muttn, custom_commands
from functions import commands as command_stats
import pytz
import time
import traceback


class Events(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.utilsCog = self.client.get_cog("Utils")
        self.failedChecksCog = self.client.get_cog("FailedChecks")
        self.lastFeatureRequest = 0
        self.lastBugReport = 0

    @commands.Cog.listener()
    async def on_connect(self):
        """
        Function called when the bot connects to Discord.
        """
        print("Connected")

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Function called when the bot is ready & done leading.
        """
        # Change status
        with open("files/status.txt", "r") as statusFile:
            status = statusFile.readline()

        await self.client.change_presence(status=discord.Status.online, activity=discord.Game(str(status)))

        # Print a message in the terminal to show that he's ready
        with open("files/readyMessage.txt", "r") as readyFile:
            readyMessage = readyFile.readline()

        print(readyMessage)

        # Add constants to the client as a botvar
        self.client.constants = constants.Live if "zandbak" not in readyMessage else constants.Zandbak

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        Function called when someone sends a message the bot can see.
        :param message: the discord.Message instance of the message
        """
        # Check if the server is locked, if so only allow me (to unlock) & Didier (to send the message) to talk
        if self.client.locked \
                and message.guild is not None \
                and str(message.author.id) != constants.myId \
                and str(message.author.id) != constants.didierId:
            # Auto unlock when someone sends a message past the current time
            if time.time() > self.client.lockedUntil:
                return await self.unlock(message.channel)

            return await self.utilsCog.removeMessage(message)

        # If FreeGamesCheck failed, remove the message & send the user a DM
        if not checks.freeGamesCheck(message):
            await self.failedChecksCog.freeGames(message)

        # Boos React to people that call him Dider
        if "dider" in message.content.lower() and str(message.author.id) not in [constants.myId, constants.didierId, constants.coolerDidierId]:
            await message.add_reaction("<:boos:629603785840263179>")

        # Check for other easter eggs
        eER = easterEggResponses.control(self.client, message)
        if eER:
            await message.channel.send(eER)

        # Check for custom commands
        custom = custom_commands.is_custom_command(message)

        if custom.id is not None:
            await message.channel.send(custom.response)

        # Earn XP & Message count
        stats.sentMessage(message)

    @commands.Cog.listener()
    async def on_command(self, ctx):
        """
        Function called whenever someone invokes a command.
        Logs commands in your terminal.
        :param ctx: Discord Context
        """
        DM = ctx.guild is None
        print("{} in {}: {}".format(ctx.author.display_name,
                                    "DM" if DM else "{} ({})".format(ctx.channel.name, ctx.guild.name),
                                    ctx.message.content))
        command_stats.updateFile(ctx)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, err):
        """
        Function called when a command throws an error.
        :param ctx: Discord Context
        :param err: the error thrown
        """
        # Zandbak Didier shouldn't spam the error logs
        if self.client.user.id == int(constants.coolerDidierId):
            raise err

        # Don't handle commands that have their own custom error handler
        if hasattr(ctx.command, 'on_error'):
            return
        # Someone just mentioned Didier without calling a real command,
        # don't care about this error
        if isinstance(err, (commands.CommandNotFound, commands.CheckFailure, commands.TooManyArguments, commands.ExpectedClosingQuoteError), ):
            pass
        # Someone used a command that was on cooldown
        elif isinstance(err, commands.CommandOnCooldown):
            await ctx.send("Je kan dit commando niet (meer) spammen.", delete_after=10)
        elif isinstance(err, commands.MessageNotFound):
            await ctx.send("Geen message gevonden die overeenkomt met het opgegeven argument.")
        elif isinstance(err, (commands.ChannelNotFound, commands.ChannelNotReadable)):
            await ctx.send("Geen channel gevonden dat overeenkomt met het opgegeven argument.")
        # Someone forgot an argument or passed an invalid argument
        elif isinstance(err, (commands.BadArgument, commands.MissingRequiredArgument, commands.UnexpectedQuoteError)):
            await ctx.send("Controleer je argumenten.")
        else:
            # Remove the InvokeCommandError because it's useless information
            x = traceback.format_exception(type(err), err, err.__traceback__)
            errorString = ""
            for line in x:
                if "direct cause of the following" in line:
                    break
                errorString += line.replace("*", "") + "\n" if line.strip() != "" else ""
            await self.sendErrorEmbed(ctx, err, errorString)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, react):
        """
        Function called when someone adds a reaction to a message.
        :param react: the RawReactionEvent associated with the reaction
        """
        # Ignore RPS adding reacts
        if self.client.get_user(react.user_id).bot:
            return
        # Feature request
        if str(react.emoji) == "➕":
            await self.sendReactEmbed(react, "Feature Request")
        # Bug report
        elif str(react.emoji) == "🐛":
            await self.sendReactEmbed(react, "Bug Report")
        # Muttn react
        elif str(react.emoji) == "<:Muttn:761551956346798111>":
            await self.addMuttn(react)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, react):
        """
        Function called when someone removes a reaction from a message.
        :param react: the RawReactionEvent associated with the reaction
        """
        # Decrease Muttn counter
        if str(react.emoji) == "<:Muttn:761551956346798111>":
            await self.removeMuttn(react)

    async def removeMuttn(self, react):
        """
        Function that decreases the Muttn counter for someone.
        :param react: the RawReactionEvent associated with the reaction
        """
        # Get the Message instance of the message
        channel = self.client.get_channel(react.channel_id)
        message = await channel.fetch_message(react.message_id)
        muttn.removeMuttn(message)

    async def addMuttn(self, react):
        """
        Function that checks the Muttn counter for a message.
        :param react: the RawReactionEvent associated with the reaction
        """
        count = -1
        # Get the Message instance of the message
        channel = self.client.get_channel(react.channel_id)
        message = await channel.fetch_message(react.message_id)

        # Get the amount of reacts on this message
        for reaction in message.reactions:
            if str(reaction.emoji) == "<:Muttn:761551956346798111>":
                count = reaction.count
                for user in await reaction.users().flatten():
                    # Remove bot reacts
                    if user.bot:
                        count -= 1
                break

        # React was removed in the milliseconds the fetch_message needs to get the info
        if count <= 0:
            return

        # Update the db
        muttn.muttn(message.author.id, count, message.id)

    def reactCheck(self, react, msg):
        """
        Function that checks if feature requests/bug reports have been sent already.
        :param react: the RawReactionEvent associated with the reaction
        :param msg: the message this react was placed on
        """
        # # Blacklist NinjaJay after spamming
        # if react.user_id in [153162010576551946]:
        #     return False

        # Don't spam DM's when something has already been reported
        # Check if the react's count is 1
        for reaction in msg.reactions:
            if reaction.emoji == react.emoji.name:
                return reaction.count == 1

    async def sendReactEmbed(self, react, messageType):
        """
        Function that sends a message in Zandbak with what's going on.
        :param react: the RawReactionEvent associated with the reaction
        :param messageType: the type of message to send
        """
        channel = self.client.get_channel(react.channel_id)
        msg = await channel.fetch_message(react.message_id)

        # Didn't pass the check, ignore it
        if not self.reactCheck(react, msg):
            return

        typeChannels = {"Feature Request": int(constants.FeatureRequests), "Bug Report": int(constants.BugReports)}

        # Add a 10 second cooldown to requests/reports to avoid spam
        # even tho apparently the people don't care
        if round(time.time()) - (
                self.lastFeatureRequest if messageType == "Feature Request" else self.lastBugReport) < 10:
            await channel.send("Je moet even wachten vooraleer je nog een {} maakt.".format(messageType.lower()))
            await msg.add_reaction("🕐")
            return
        # Report on an empty message
        elif msg.content == "":
            await channel.send("Dit bericht bevat geen tekst.")
            await msg.add_reaction("❌")
            return

        # Update the variables
        if messageType == "Feature Request":
            self.lastFeatureRequest = round(time.time())
        else:
            self.lastBugReport = round(time.time())

        # Ignore people reacting on Didier's messages
        if str(msg.author.id) != constants.didierId:
            # Get the user's User instance & the channel to send the message to
            COC = self.client.get_guild(int(constants.CallOfCode))
            user = COC.get_member(react.user_id)
            targetChannel = self.client.get_channel(typeChannels[messageType])

            await targetChannel.send("{} door **{}** in **#{}** ({}):\n``{}``\n{}".format(
                                         messageType,
                                         user.display_name,
                                         channel.name if str(channel.type) != "private" else "DM",
                                         channel.guild.name if str(channel.type) != "private" else "DM",
                                         msg.content, msg.jump_url
                                     ))
            await msg.add_reaction("✅")

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """
        Function called when a message is edited,
        so people can't edit messages in FreeGames to cheat the system.
        :param before: the message before it was edited
        :param after: the message after it was edited
        """
        # Run the message through the checks again
        if not checks.freeGamesCheck(after):
            await self.failedChecksCog.freeGames(after)

    async def sendErrorEmbed(self, ctx, error: Exception, trace):
        """
        Function that sends an error embed in #ErrorLogs.
        :param ctx: Discord Context
        :param error: the error thrown
        :param trace: the stacktrace of the error
        """
        embed = discord.Embed(colour=discord.Colour.red())
        embed.set_author(name="Error")
        embed.add_field(name="Command:", value="{} in {}: {}".format(ctx.author.display_name,
                                                                     ctx.channel.name if str(
                                                                         ctx.channel.type) != "private" else "DM",
                                                                     ctx.message.content), inline=False)
        embed.add_field(name="Error:", value=str(error)[:1024], inline=False)
        embed.add_field(name="Message:", value=str(trace)[:1024], inline=False)

        # Add remaining parts in extra fields
        # (embed field limits)
        if len(str(trace)) < 5500:
            trace_split = [str(trace)[i:i + 1024] for i in range(1024, len(str(trace)), 1024)]
            for spl in trace_split:
                embed.add_field(name="\u200b", value=spl, inline=False)

        errorChannel = self.client.get_channel(762668505455132722)
        await errorChannel.send(embed=embed)

    @commands.command(hidden=True)
    @commands.check(checks.isMe)
    async def lock(self, ctx, until=None):
        """
        Command that locks the server during online exams.
        :param ctx: Discord Context
        :param until: the timestamp until which to lock (HH:MM)
        """
        # No timestamp passed
        if until is None:
            return

        until = until.split(":")

        # Create timestamps
        now = datetime.datetime.now()
        untilTimestamp = time.time()

        # Gets the current amount of minutes into the day
        nowMinuteCount = (now.hour * 60) + now.minute

        # Gets the target amount of minutes into the day
        untilMinuteCount = (int(until[0]) * 60) + int(until[1])

        # Adds the remaining seconds onto the current time to calculate the end of the lock
        untilTimestamp += (60 * (untilMinuteCount - nowMinuteCount)) - now.second

        self.client.locked = True
        self.client.lockedUntil = round(untilTimestamp)

        await ctx.send("De server wordt gelocked tot **{}**.".format(
            datetime.datetime.fromtimestamp(untilTimestamp,
                                            pytz.timezone("Europe/Brussels")
                                            ).strftime('%H:%M:%S')))

    @commands.command(hidden=True)
    @commands.check(checks.isMe)
    async def unlock(self, ctx):
        """
        Command to unlock the server manually before the timer is over.
        :param ctx: Discord Context
        """
        self.client.locked = False
        self.client.lockedUntil = -1
        await ctx.send("De server is niet langer gelocked.")


def setup(client):
    client.add_cog(Events(client))
