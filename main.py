import logging
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

    didier_log = logging.getLogger("didier")

    handler = RotatingFileHandler(settings.LOGFILE, mode="a", maxBytes=max_log_size, backupCount=5)
    handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s]: %(message)s"))
    handler.setLevel(logging.INFO)

    didier_log.addHandler(handler)

    logging.getLogger("discord").setLevel(logging.ERROR)


async def main():
    """Do some setup & checks, and then run the bot"""
    setup_logging()
    await ensure_latest_migration()
    await run_bot()


if __name__ == "__main__":
    asyncio.run(main())
