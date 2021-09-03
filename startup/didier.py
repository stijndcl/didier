from data.snipe import Snipe
from discord.ext import commands, ipc
from dislash import InteractionClient
import os
from settings import HOST_IPC
from startup.init_files import check_all
from typing import Dict


class Didier(commands.Bot):
    """
    Main Bot class for Didier
    """
    # Reference to interactions client
    interactions: InteractionClient

    # Dict to store the most recent Snipe info per channel
    snipe: Dict[int, Snipe] = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._host_ipc = HOST_IPC

        # IPC Server
        # TODO secret key
        self.ipc = ipc.Server(self, secret_key="SOME_SECRET_KEY") if self._host_ipc else None

        # Cogs that should be loaded before the others
        self._preload = ("ipc", "utils", "failedchecks", "events",)

        # Remove default help command
        self.remove_command("help")

        # Create interactions client
        self.interactions = InteractionClient(self, test_guilds=[728361030404538488, 880175869841277008])

        # Load all extensions
        self.init_extensions()

        # Check missing files
        check_all()

    def init_extensions(self):
        # Load initial extensions
        for ext in self._preload:
            self.load_extension(f"cogs.{ext}")

        # Load all remaining cogs
        self._init_directory("./cogs")

    def _init_directory(self, path: str):
        """
        Load all cogs from a directory
        """
        # Path to pass into load_extension
        load_path = path[2:].replace("/", ".")

        for file in os.listdir(path):
            # Python file
            if file.endswith(".py"):
                if not file.startswith(self._preload):
                    self.load_extension(f"{load_path}.{file[:-3]}")
            elif os.path.isdir(new_path := f"{path}/{file}"):
                # Subdirectory
                # Also walrus operator hype
                self._init_directory(new_path)

    async def on_ipc_ready(self):
        print("IPC server is ready.")

    async def on_ipc_error(self, endpoint, error):
        print(endpoint, "raised", error)
