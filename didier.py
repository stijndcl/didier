import discord
from discord.ext import commands, ipc
from dotenv import load_dotenv
from functions.prefixes import get_prefix
import os


# TODO pass option (bool) that launches IPC
#   so there's no server running if it's not required
class Didier(commands.Bot):
    """
    Main Bot class for Didier
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # IPC Server
        # TODO secret key
        self.ipc = ipc.Server(self, secret_key="SOME_SECRET_KEY")

        # Cogs that should be loaded before the others
        self.preload = ("ipc", "utils", "failedchecks", "events",)

        # Remove default help command
        self.remove_command("help")

        self.init_extensions()

    def init_extensions(self):
        # Load initial extensions
        for ext in self.preload:
            self.load_extension(f"cogs.{ext}")

        # Load all remaining cogs
        for file in os.listdir("./cogs"):
            if file.endswith(".py") and not (file.startswith(self.preload)):
                self.load_extension("cogs.{}".format(file[:-3]))

    async def on_ipc_ready(self):
        print("IPC server is ready.")

    async def on_ipc_error(self, endpoint, error):
        print(endpoint, "raised", error)


if __name__ == "__main__":
    load_dotenv(verbose=True)

    # Configure intents (1.5.0)
    intents = discord.Intents.default()
    intents.members = True

    client = Didier(command_prefix=get_prefix, case_insensitive=True, intents=intents)

    # Get the token out of the file & run the bot
    with open("files/client.txt", "r") as fp:
        token = fp.readline()

    client.ipc.start()
    client.run(token)
