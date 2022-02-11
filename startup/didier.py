from data.snipe import Snipe
from discord.ext import commands
import os
from startup.init_files import check_all
from typing import Dict


class Didier(commands.Bot):
    """
    Main Bot class for Didier
    """
    # Dict to store the most recent Snipe info per channel
    snipe: Dict[int, Snipe] = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Cogs that should be loaded before the others
        self._preload = ("utils", "failedchecks", "events",)

        # Remove default help command
        self.remove_command("help")

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
