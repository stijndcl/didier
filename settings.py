from typing import Optional

from environs import Env

# Read the .env file (if present)
env = Env()
env.read_env()

__all__ = [
    "SANDBOX",
    "TESTING",
    "LOGFILE",
    "POSTGRES_DB",
    "POSTGRES_USER",
    "POSTGRES_PASS",
    "POSTGRES_HOST",
    "POSTGRES_PORT",
    "DISCORD_TOKEN",
    "DISCORD_READY_MESSAGE",
    "DISCORD_STATUS_MESSAGE",
    "DISCORD_TEST_GUILDS",
    "DISCORD_BOOS_REACT",
    "DISCORD_CUSTOM_COMMAND_PREFIX",
    "UFORA_ANNOUNCEMENTS_CHANNEL",
    "UFORA_RSS_TOKEN",
    "URBAN_DICTIONARY_TOKEN",
    "IMGFLIP_NAME",
    "IMGFLIP_PASSWORD",
]


"""General config"""
SANDBOX: bool = env.bool("SANDBOX", True)
TESTING: bool = env.bool("TESTING", False)
LOGFILE: str = env.str("LOGFILE", "didier.log")
SEMESTER: int = env.int("SEMESTER", 2)
YEAR: int = env.int("YEAR", 3)

"""Database"""
# MongoDB
MONGO_DB: str = env.str("MONGO_DB", "didier")
MONGO_USER: str = env.str("MONGO_USER", "root")
MONGO_PASS: str = env.str("MONGO_PASS", "root")
MONGO_HOST: str = env.str("MONGO_HOST", "localhost")
MONGO_PORT: int = env.int("MONGO_PORT", "27017")

# PostgreSQL
POSTGRES_DB: str = env.str("POSTGRES_DB", "didier")
POSTGRES_USER: str = env.str("POSTGRES_USER", "postgres")
POSTGRES_PASS: str = env.str("POSTGRES_PASS", "")
POSTGRES_HOST: str = env.str("POSTGRES_HOST", "localhost")
POSTGRES_PORT: int = env.int("POSTGRES_PORT", "5432")

"""Discord"""
DISCORD_TOKEN: str = env.str("DISCORD_TOKEN")
DISCORD_READY_MESSAGE: str = env.str("DISCORD_READY_MESSAGE", "I'M READY I'M READY I'M READY")
DISCORD_STATUS_MESSAGE: str = env.str("DISCORD_STATUS_MESSAGE", "with your Didier Dinks.")
DISCORD_TEST_GUILDS: list[int] = env.list("DISCORD_TEST_GUILDS", [], subcast=int)
DISCORD_OWNER_GUILDS: Optional[list[int]] = env.list("DISCORD_OWNER_GUILDS", [], subcast=int) or None
DISCORD_BOOS_REACT: str = env.str("DISCORD_BOOS_REACT", "<:boos:629603785840263179>")
DISCORD_CUSTOM_COMMAND_PREFIX: str = env.str("DISCORD_CUSTOM_COMMAND_PREFIX", "?")
BIRTHDAY_ANNOUNCEMENT_CHANNEL: Optional[int] = env.int("BIRTHDAY_ANNOUNCEMENT_CHANNEL", None)
ERRORS_CHANNEL: Optional[int] = env.int("ERRORS_CHANNEL", None)
UFORA_ANNOUNCEMENTS_CHANNEL: Optional[int] = env.int("UFORA_ANNOUNCEMENTS_CHANNEL", None)

"""API Keys"""
UFORA_RSS_TOKEN: Optional[str] = env.str("UFORA_RSS_TOKEN", None)
URBAN_DICTIONARY_TOKEN: Optional[str] = env.str("URBAN_DICTIONARY_TOKEN", None)
IMGFLIP_NAME: Optional[str] = env.str("IMGFLIP_NAME", None)
IMGFLIP_PASSWORD: Optional[str] = env.str("IMGFLIP_PASSWORD", None)
