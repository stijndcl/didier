import logging
import sys
from logging.handlers import RotatingFileHandler

import asyncio

import settings
from database.migrations import ensure_latest_migration
from didier import Didier


async def run_bot():
    """Run Didier"""
    didier = Didier()
    await didier.start(settings.DISCORD_TOKEN)


def setup_logging():
    """Configure custom loggers"""
    max_log_size = 32 * 1024 * 1024

    # Configure Didier handler
    didier_log = logging.getLogger("didier")

    didier_handler = RotatingFileHandler(settings.LOGFILE, mode="a", maxBytes=max_log_size, backupCount=5)
    didier_handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s]: %(message)s"))

    didier_log.addHandler(didier_handler)
    didier_log.setLevel(logging.INFO)

    # Configure discord handler
    discord_log = logging.getLogger("discord")

    # Make dev print to stderr instead, so you don't have to watch the file
    if settings.SANDBOX:
        discord_handler = logging.StreamHandler(sys.stderr)
    else:
        discord_handler = RotatingFileHandler("discord.log", mode="a", maxBytes=max_log_size, backupCount=5)

    discord_handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"))
    discord_log.addHandler(discord_handler)


async def main():
    """Do some setup & checks, and then run the bot"""
    setup_logging()
    await ensure_latest_migration()
    await run_bot()


if __name__ == "__main__":
    asyncio.run(main())
