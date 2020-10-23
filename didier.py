import discord
from discord.ext import commands
from dotenv import load_dotenv
import os


load_dotenv(verbose=True)


# All possible prefixes
# When_mentioned_or doesn't count for spaces so can't use that
prefixes = ["didier ", "Didier ", "DIDIER ", "big d ", "Big d ", "Big D ", "BIG D ", "<@!680510935164911730> ",
            "didier", "Didier", "DIDIER", "big d", "Big d", "Big D", "BIG D", "<@!680510935164911730>"]

# Configure intents (1.5.0)
intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix=prefixes, case_insensitive=True, intents=intents)
client.prefixes = prefixes

# Remove default help because it sucks & I made my own
client.remove_command("help")

# Load utils first so it can be used in other places & it's not None
client.load_extension("cogs.utils")
client.load_extension("cogs.failedchecks")
client.load_extension("cogs.events")

# Load all remaining cogs
for file in os.listdir("./cogs"):
    if file.endswith(".py") and not (file.startswith(("utils", "failedchecks", "events"),)):
        client.load_extension("cogs.{}".format(file[:-3]))

# Get the token out of the file & run the bot
with open("files/client.txt", "r") as fp:
    token = fp.readline()
client.run(token)
