import discord
from dotenv import load_dotenv
from functions.prefixes import get_prefix
from settings import TOKEN
from startup.didier import Didier

if __name__ == "__main__":
    load_dotenv(verbose=True)

    # Configure intents (1.5.0)
    intents = discord.Intents.default()
    intents.members = True

    client = Didier(command_prefix=get_prefix, case_insensitive=True, intents=intents)

    if client.ipc is not None:
        client.ipc.start()

    client.run(TOKEN)
