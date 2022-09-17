from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship

from database import enums

Base = declarative_base()


__all__ = [
    "Base",
    "Bank",
    "Birthday",
    "Bookmark",
    "CustomCommand",
    "CustomCommandAlias",
    "DadJoke",
    "Deadline",
    "Link",
    "MemeTemplate",
    "NightlyData",
    "Task",
    "UforaAnnouncement",
    "UforaCourse",
    "UforaCourseAlias",
    "User",
    "WordleGuess",
    "WordleStats",
    "WordleWord",
]


class Bank(Base):
    """A user's currency information"""

    __tablename__ = "bank"

    bank_id: int = Column(Integer, primary_key=True)
    user_id: int = Column(BigInteger, ForeignKey("users.user_id"))

    dinks: int = Column(BigInteger, server_default="0", nullable=False)
    invested: int = Column(BigInteger, server_default="0", nullable=False)

    # Interest rate
    interest_level: int = Column(Integer, server_default="1", nullable=False)

    # Maximum amount that can be stored in the bank
    capacity_level: int = Column(Integer, server_default="1", nullable=False)

    # Maximum amount that can be robbed
    rob_level: int = Column(Integer, server_default="1", nullable=False)

    user: User = relationship("User", uselist=False, back_populates="bank", lazy="selectin")


class Birthday(Base):
    """A user's birthday"""

    __tablename__ = "birthdays"

    birthday_id: int = Column(Integer, primary_key=True)
    user_id: int = Column(BigInteger, ForeignKey("users.user_id"))
    birthday: date = Column(Date, nullable=False)

    user: User = relationship("User", uselist=False, back_populates="birthday", lazy="selectin")


class Bookmark(Base):
    """A bookmark to a given message"""

    __tablename__ = "bookmarks"
    __table_args__ = (UniqueConstraint("user_id", "label"),)

    bookmark_id: int = Column(Integer, primary_key=True)
    label: str = Column(Text, nullable=False)
    jump_url: str = Column(Text, nullable=False)
    user_id: int = Column(BigInteger, ForeignKey("users.user_id"))

    user: User = relationship("User", back_populates="bookmarks", uselist=False, lazy="selectin")


class CustomCommand(Base):
    """Custom commands to fill the hole Dyno couldn't"""

    __tablename__ = "custom_commands"

    command_id: int = Column(Integer, primary_key=True)
    name: str = Column(Text, nullable=False, unique=True)
    indexed_name: str = Column(Text, nullable=False, index=True)
    response: str = Column(Text, nullable=False)

    aliases: list[CustomCommandAlias] = relationship(
        "CustomCommandAlias", back_populates="command", uselist=True, cascade="all, delete-orphan", lazy="selectin"
    )


class CustomCommandAlias(Base):
    """Aliases for custom commands"""

    __tablename__ = "custom_command_aliases"

    alias_id: int = Column(Integer, primary_key=True)
    alias: str = Column(Text, nullable=False, unique=True)
    indexed_alias: str = Column(Text, nullable=False, index=True)
    command_id: int = Column(Integer, ForeignKey("custom_commands.command_id"))

    command: CustomCommand = relationship("CustomCommand", back_populates="aliases", uselist=False, lazy="selectin")


class DadJoke(Base):
    """When I finally understood asymptotic notation, it was a big "oh" moment"""

    __tablename__ = "dad_jokes"

    dad_joke_id: int = Column(Integer, primary_key=True)
    joke: str = Column(Text, nullable=False)


class Deadline(Base):
    """A deadline for a university project"""

    __tablename__ = "deadlines"

    deadline_id: int = Column(Integer, primary_key=True)
    course_id: int = Column(Integer, ForeignKey("ufora_courses.course_id"))
    name: str = Column(Text, nullable=False)
    deadline: datetime = Column(DateTime(timezone=True), nullable=False)

    course: UforaCourse = relationship("UforaCourse", back_populates="deadlines", uselist=False, lazy="selectin")


class Link(Base):
    """Useful links that go useful places"""

    __tablename__ = "links"

    link_id: int = Column(Integer, primary_key=True)
    name: str = Column(Text, nullable=False, unique=True)
    url: str = Column(Text, nullable=False)


class MemeTemplate(Base):
    """A meme template for the Imgflip API"""

    __tablename__ = "meme"

    meme_id: int = Column(Integer, primary_key=True)
    name: str = Column(Text, nullable=False, unique=True)
    template_id: int = Column(Integer, nullable=False, unique=True)
    field_count: int = Column(Integer, nullable=False)


class NightlyData(Base):
    """Data for a user's Nightly stats"""

    __tablename__ = "nightly_data"

    nightly_id: int = Column(Integer, primary_key=True)
    user_id: int = Column(BigInteger, ForeignKey("users.user_id"))
    last_nightly: Optional[date] = Column(Date, nullable=True)
    count: int = Column(Integer, server_default="0", nullable=False)

    user: User = relationship("User", back_populates="nightly_data", uselist=False, lazy="selectin")


class Task(Base):
    """A Didier task"""

    __tablename__ = "tasks"

    task_id: int = Column(Integer, primary_key=True)
    task: enums.TaskType = Column(Enum(enums.TaskType), nullable=False, unique=True)
    previous_run: datetime = Column(DateTime(timezone=True), nullable=True)


class UforaCourse(Base):
    """A course on Ufora"""

    __tablename__ = "ufora_courses"

    course_id: int = Column(Integer, primary_key=True)
    name: str = Column(Text, nullable=False, unique=True)
    code: str = Column(Text, nullable=False, unique=True)
    year: int = Column(Integer, nullable=False)
    compulsory: bool = Column(Boolean, server_default="1", nullable=False)
    role_id: Optional[int] = Column(BigInteger, nullable=True, unique=False)
    overarching_role_id: Optional[int] = Column(BigInteger, nullable=True, unique=False)
    log_announcements: bool = Column(Boolean, server_default="0", nullable=False)

    announcements: list[UforaAnnouncement] = relationship(
        "UforaAnnouncement", back_populates="course", cascade="all, delete-orphan", lazy="selectin"
    )
    aliases: list[UforaCourseAlias] = relationship(
        "UforaCourseAlias", back_populates="course", cascade="all, delete-orphan", lazy="selectin"
    )
    deadlines: list[Deadline] = relationship(
        "Deadline", back_populates="course", cascade="all, delete-orphan", lazy="selectin"
    )


class UforaCourseAlias(Base):
    """An alias for a course on Ufora that we use to refer to them"""

    __tablename__ = "ufora_course_aliases"

    alias_id: int = Column(Integer, primary_key=True)
    alias: str = Column(Text, nullable=False, unique=True)
    course_id: int = Column(Integer, ForeignKey("ufora_courses.course_id"))

    course: UforaCourse = relationship("UforaCourse", back_populates="aliases", uselist=False, lazy="selectin")


class UforaAnnouncement(Base):
    """An announcement sent on Ufora"""

    __tablename__ = "ufora_announcements"

    announcement_id: int = Column(Integer, primary_key=True)
    course_id: int = Column(Integer, ForeignKey("ufora_courses.course_id"))
    publication_date: date = Column(Date)

    course: UforaCourse = relationship("UforaCourse", back_populates="announcements", uselist=False, lazy="selectin")


class User(Base):
    """A Didier user"""

    __tablename__ = "users"

    user_id: int = Column(BigInteger, primary_key=True)

    bank: Bank = relationship(
        "Bank", back_populates="user", uselist=False, lazy="selectin", cascade="all, delete-orphan"
    )
    birthday: Optional[Birthday] = relationship(
        "Birthday", back_populates="user", uselist=False, lazy="selectin", cascade="all, delete-orphan"
    )
    bookmarks: list[Bookmark] = relationship(
        "Bookmark", back_populates="user", uselist=True, lazy="selectin", cascade="all, delete-orphan"
    )
    nightly_data: NightlyData = relationship(
        "NightlyData", back_populates="user", uselist=False, lazy="selectin", cascade="all, delete-orphan"
    )
    wordle_guesses: list[WordleGuess] = relationship(
        "WordleGuess", back_populates="user", uselist=True, lazy="selectin", cascade="all, delete-orphan"
    )
    wordle_stats: WordleStats = relationship(
        "WordleStats", back_populates="user", uselist=False, lazy="selectin", cascade="all, delete-orphan"
    )


class WordleGuess(Base):
    """A user's Wordle guesses for today"""

    __tablename__ = "wordle_guesses"

    wordle_guess_id: int = Column(Integer, primary_key=True)
    user_id: int = Column(BigInteger, ForeignKey("users.user_id"))
    guess: str = Column(Text, nullable=False)

    user: User = relationship("User", back_populates="wordle_guesses", uselist=False, lazy="selectin")


class WordleStats(Base):
    """Stats about a user's wordle performance"""

    __tablename__ = "wordle_stats"

    wordle_stats_id: int = Column(Integer, primary_key=True)
    user_id: int = Column(BigInteger, ForeignKey("users.user_id"))
    last_win: Optional[date] = Column(Date, nullable=True)
    games: int = Column(Integer, server_default="0", nullable=False)
    wins: int = Column(Integer, server_default="0", nullable=False)
    current_streak: int = Column(Integer, server_default="0", nullable=False)
    highest_streak: int = Column(Integer, server_default="0", nullable=False)

    user: User = relationship("User", back_populates="wordle_stats", uselist=False, lazy="selectin")


class WordleWord(Base):
    """The current Wordle word"""

    __tablename__ = "wordle_word"

    word_id: int = Column(Integer, primary_key=True)
    word: str = Column(Text, nullable=False)
    day: date = Column(Date, nullable=False, unique=True)