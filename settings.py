from typing import List

from dotenv import load_dotenv
import os


load_dotenv()


def _to_bool(value: str) -> bool:
    """
    Env variables are strings so this converts them to booleans
    """
    return value.lower() in ["true", "1", "y", "yes"]


# Sandbox or live
SANDBOX = _to_bool(os.getenv("SANDBOX", "true"))

# Tokens & API keys
URBANDICTIONARY = os.getenv("URBANDICTIONARY", "")
IMGFLIP_NAME = os.getenv("IMGFLIPNAME", "")
IMGFLIP_PASSWORD = os.getenv("IMGFLIPPASSWORD", "")

# Database credentials
DB_USERNAME = os.getenv("DBUSERNAME", "")
DB_PASSWORD = os.getenv("DBPASSWORD", "")
DB_HOST = os.getenv("DBHOST", "")
DB_NAME = os.getenv("DBNAME", "")

# Discord-related
TOKEN = os.getenv("TOKEN", "")
HOST_IPC = _to_bool(os.getenv("HOSTIPC", "false"))
READY_MESSAGE = os.getenv("READYMESSAGE", "I'M READY I'M READY I'M READY I'M READY")  # Yes, this is a Spongebob reference
STATUS_MESSAGE = os.getenv("STATUSMESSAGE", "with your Didier Dinks.")

# Guilds to test slash commands in
# Ex: 123,456,789
_guilds = os.getenv("SLASHTESTGUILDS", "").replace(" ", "")
SLASH_TEST_GUILDS: List[int] = list(map(lambda x: int(x), _guilds.split(","))) if _guilds else []
