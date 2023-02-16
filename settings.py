from dataclasses import dataclass
from enum import Enum
from typing import Optional

from environs import Env

# Read the .env file (if present)
env = Env()
env.read_env()

__all__ = [
    "SANDBOX",
    "TESTING",
    "LOGFILE",
    "SEMESTER",
    "YEAR",
    "MENU_TIMEOUT",
    "EASTER_EGG_CHANCE",
    "REMINDER_PRE",
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
    "ERRORS_CHANNEL",
    "FREE_GAMES_CHANNEL",
    "UFORA_ANNOUNCEMENTS_CHANNEL",
    "UFORA_RSS_TOKEN",
    "IMGFLIP_NAME",
    "IMGFLIP_PASSWORD",
    "ScheduleType",
    "ScheduleInfo",
    "SCHEDULE_DATA",
]


"""General config"""
SANDBOX: bool = env.bool("SANDBOX", True)
TESTING: bool = env.bool("TESTING", False)
LOGFILE: str = env.str("LOGFILE", "didier.log")
SEMESTER: int = env.int("SEMESTER", 2)
YEAR: int = env.int("YEAR", 3)
MENU_TIMEOUT: int = env.int("MENU_TIMEOUT", 30)
EASTER_EGG_CHANCE: int = env.int("EASTER_EGG_CHANCE", 15)
REMINDER_PRE: int = env.int("REMINDER_PRE", 15)

"""Database"""
# PostgreSQL
POSTGRES_DB: str = env.str("POSTGRES_DB", "didier_dev")
POSTGRES_USER: str = env.str("POSTGRES_USER", "postgres")
POSTGRES_PASS: str = env.str("POSTGRES_PASS", "postgres")
POSTGRES_HOST: str = env.str("POSTGRES_HOST", "localhost")
POSTGRES_PORT: int = env.int("POSTGRES_PORT", "5432")

"""Discord"""
DISCORD_TOKEN: str = env.str("DISCORD_TOKEN")
DISCORD_READY_MESSAGE: str = env.str("DISCORD_READY_MESSAGE", "I'M READY I'M READY I'M READY")
DISCORD_STATUS_MESSAGE: str = env.str("DISCORD_STATUS_MESSAGE", "with your Didier Dinks.")
DISCORD_MAIN_GUILD: int = env.int("DISCORD_MAIN_GUILD")
DISCORD_TEST_GUILDS: list[int] = env.list("DISCORD_TEST_GUILDS", [], subcast=int)
DISCORD_OWNER_GUILDS: Optional[list[int]] = env.list("DISCORD_OWNER_GUILDS", [], subcast=int) or None
DISCORD_BOOS_REACT: str = env.str("DISCORD_BOOS_REACT", "<:boos:629603785840263179>")
DISCORD_CUSTOM_COMMAND_PREFIX: str = env.str("DISCORD_CUSTOM_COMMAND_PREFIX", "?")
BIRTHDAY_ANNOUNCEMENT_CHANNEL: Optional[int] = env.int("BIRTHDAY_ANNOUNCEMENT_CHANNEL", None)
ERRORS_CHANNEL: Optional[int] = env.int("ERRORS_CHANNEL", None)
FREE_GAMES_CHANNEL: Optional[int] = env.int("FREE_GAMES_CHANNEL", None)
UFORA_ANNOUNCEMENTS_CHANNEL: Optional[int] = env.int("UFORA_ANNOUNCEMENTS_CHANNEL", None)

"""Discord Role ID's"""
BA3_ROLE: Optional[int] = env.int("BA3_ROLE", 891743208248324196)
MA_CS_1_ROLE: Optional[int] = env.int("MA_CS_1_ROLE", 1023293447387496570)
MA_CS_2_ROLE: Optional[int] = env.int("MA_CS_2_ROLE", 1023302736210567208)
MA_CS_ENG_1_ROLE: Optional[int] = env.int("MA_CS_ENG_1_ROLE", 1023278462733127710)
MA_CS_ENG_2_ROLE: Optional[int] = env.int("MA_CS_ENG_2_ROLE", 1023300434800164914)

"""API Keys"""
UFORA_RSS_TOKEN: Optional[str] = env.str("UFORA_RSS_TOKEN", None)
IMGFLIP_NAME: Optional[str] = env.str("IMGFLIP_NAME", None)
IMGFLIP_PASSWORD: Optional[str] = env.str("IMGFLIP_PASSWORD", None)

"""Schedule URLs"""
BA3_SCHEDULE_URL: Optional[str] = env.str("BA3_SCHEDULE_URL", None)
MA_CS_1_SCHEDULE_URL: Optional[str] = env.str("MA_CS_1_SCHEDULE_URL", None)
MA_CS_2_SCHEDULE_URL: Optional[str] = env.str("MA_CS_2_SCHEDULE_URL", None)
MA_CS_ENG_1_SCHEDULE_URL: Optional[str] = env.str("MA_CS_ENG_1_SCHEDULE_URL", None)
MA_CS_ENG_2_SCHEDULE_URL: Optional[str] = env.str("MA_CS_ENG_2_SCHEDULE_URL", None)


"""Computed properties"""


class ScheduleType(str, Enum):
    """Enum to differentiate schedules"""

    BA3 = "ba3"
    MA_CS_1 = "ma_cs_1"
    MA_CS_2 = "ma_cs_2"
    MA_CS_ENG_1 = "ma_cs_eng_1"
    MA_CS_ENG_2 = "ma_cs_eng_2"


@dataclass
class ScheduleInfo:
    """Dataclass to hold and combine some information about schedule-related settings"""

    role_id: Optional[int]
    schedule_url: Optional[str]
    name: Optional[str] = None


SCHEDULE_DATA = [
    ScheduleInfo(name=ScheduleType.BA3, role_id=BA3_ROLE, schedule_url=BA3_SCHEDULE_URL),
    ScheduleInfo(name=ScheduleType.MA_CS_1, role_id=MA_CS_1_ROLE, schedule_url=MA_CS_1_SCHEDULE_URL),
    ScheduleInfo(name=ScheduleType.MA_CS_2, role_id=MA_CS_2_ROLE, schedule_url=MA_CS_2_SCHEDULE_URL),
    ScheduleInfo(name=ScheduleType.MA_CS_ENG_1, role_id=MA_CS_ENG_1_ROLE, schedule_url=MA_CS_ENG_1_SCHEDULE_URL),
    ScheduleInfo(name=ScheduleType.MA_CS_ENG_2, role_id=MA_CS_ENG_2_ROLE, schedule_url=MA_CS_ENG_2_SCHEDULE_URL),
]
