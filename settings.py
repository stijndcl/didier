from typing import Optional

from environs import Env

# Read the .env file (if present)
env = Env()
env.read_env()

"""General config"""
SANDBOX: bool = env.bool("SANDBOX", True)
LOGFILE: str = env.str("LOGFILE", "didier.log")
TESTING: bool = env.bool("TESTING", False)

"""Database"""
DB_NAME: str = env.str("DB_NAME", "didier")
DB_USERNAME: str = env.str("DB_USERNAME", "postgres")
DB_PASSWORD: str = env.str("DB_PASSWORD", "")
DB_HOST: str = env.str("DB_HOST", "localhost")
DB_PORT: int = env.int("DB_PORT", "5432")
DB_TEST_SQLITE: bool = env.bool("DB_TEST_SQLITE", True)

"""Discord"""
DISCORD_TOKEN: str = env.str("DISC_TOKEN")
DISCORD_READY_MESSAGE: str = env.str("DISC_READY_MESSAGE", "I'M READY I'M READY I'M READY")
DISCORD_STATUS_MESSAGE: str = env.str("DISC_STATUS_MESSAGE", "with your Didier Dinks.")
DISCORD_TEST_GUILDS: list[int] = env.list("DISC_TEST_GUILDS", [], subcast=int)
DISCORD_BOOS_REACT: str = env.str("DISC_BOOS_REACT", "<:boos:629603785840263179>")
DISCORD_CUSTOM_COMMAND_PREFIX: str = env.str("DISC_CUSTOM_COMMAND_PREFIX", "?")
UFORA_ANNOUNCEMENTS_CHANNEL: Optional[int] = env.int("UFORA_ANNOUNCEMENTS_CHANNEL", None)

"""API Keys"""
UFORA_RSS_TOKEN: Optional[str] = env.str("UFORA_RSS_TOKEN", None)
