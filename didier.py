import discord
from functions.prefixes import get_prefix
from settings import STATUS_MESSAGE, TOKEN
from startup.didier import Didier

if __name__ == "__main__":
    # Activities
    activity = discord.Activity(type=discord.ActivityType.playing, name=STATUS_MESSAGE)
    status = discord.Status.online

    # Configure intents (1.5.0)
    intents = discord.Intents.default()
    intents.members = True

    client = Didier(command_prefix=get_prefix, case_insensitive=True, intents=intents, activity=activity, status=status)
    client.run(TOKEN)
