from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import BigInteger, ForeignKey, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import DateTime

from database import enums

__all__ = [
    "Base",
    "Bank",
    "BankSavings",
    "Birthday",
    "Bookmark",
    "CommandStats",
    "CustomCommand",
    "CustomCommandAlias",
    "DadJoke",
    "Deadline",
    "EasterEgg",
    "Event",
    "FreeGame",
    "GitHubLink",
    "Jail",
    "Link",
    "MemeTemplate",
    "NightlyData",
    "Reminder",
    "Task",
    "UforaAnnouncement",
    "UforaCourse",
    "UforaCourseAlias",
    "User",
]


class Base(DeclarativeBase):
    """Required base class for all tables"""

    # Make all DateTimes timezone-aware
    type_annotation_map = {datetime: DateTime(timezone=True)}


class Bank(Base):
    """A user's currency information"""

    __tablename__ = "bank"

    bank_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"))

    dinks: Mapped[int] = mapped_column(BigInteger, server_default="0", nullable=False)

    # Interest rate
    interest_level: Mapped[int] = mapped_column(server_default="1", nullable=False)

    # Maximum amount that can be stored in the bank
    capacity_level: Mapped[int] = mapped_column(server_default="1", nullable=False)

    # Maximum amount that can be robbed
    rob_level: Mapped[int] = mapped_column(server_default="1", nullable=False)

    user: Mapped[User] = relationship(uselist=False, back_populates="bank", lazy="selectin")


class BankSavings(Base):
    """Savings information for a user's bank"""

    __tablename__ = "savings"

    savings_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"))

    saved: Mapped[int] = mapped_column(BigInteger, server_default="0", nullable=False)
    daily_minimum: Mapped[int] = mapped_column(BigInteger, server_default="0", nullable=False)

    user: Mapped[User] = relationship(uselist=False, back_populates="savings", lazy="selectin")


class Birthday(Base):
    """A user's birthday"""

    __tablename__ = "birthdays"

    birthday_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"))
    birthday: Mapped[date] = mapped_column(nullable=False)

    user: Mapped[User] = relationship(uselist=False, back_populates="birthday", lazy="selectin")


class Bookmark(Base):
    """A bookmark to a given message"""

    __tablename__ = "bookmarks"
    __table_args__ = (UniqueConstraint("user_id", "label"),)

    bookmark_id: Mapped[int] = mapped_column(primary_key=True)
    label: Mapped[str] = mapped_column(nullable=False)
    jump_url: Mapped[str] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"))

    user: Mapped[User] = relationship(back_populates="bookmarks", uselist=False, lazy="selectin")


class CommandStats(Base):
    """Metrics on how often commands are used"""

    __tablename__ = "command_stats"
    command_stats_id: Mapped[int] = mapped_column(primary_key=True)
    command: Mapped[str] = mapped_column(nullable=False)
    timestamp: Mapped[datetime] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"))
    slash: Mapped[bool] = mapped_column(nullable=False)
    context_menu: Mapped[bool] = mapped_column(nullable=False)

    user: Mapped[User] = relationship(back_populates="command_stats", uselist=False, lazy="selectin")


class CustomCommand(Base):
    """Custom commands to fill the hole Dyno couldn't"""

    __tablename__ = "custom_commands"

    command_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    indexed_name: Mapped[str] = mapped_column(nullable=False, index=True)
    response: Mapped[str] = mapped_column(nullable=False)

    aliases: Mapped[List[CustomCommandAlias]] = relationship(
        back_populates="command", uselist=True, cascade="all, delete-orphan", lazy="selectin"
    )


class CustomCommandAlias(Base):
    """Aliases for custom commands"""

    __tablename__ = "custom_command_aliases"

    alias_id: Mapped[int] = mapped_column(primary_key=True)
    alias: Mapped[str] = mapped_column(nullable=False, unique=True)
    indexed_alias: Mapped[str] = mapped_column(nullable=False, index=True)
    command_id: Mapped[int] = mapped_column(ForeignKey("custom_commands.command_id"))

    command: Mapped[CustomCommand] = relationship(back_populates="aliases", uselist=False, lazy="selectin")


class DadJoke(Base):
    """When I finally understood asymptotic notation, it was a big "oh" moment"""

    __tablename__ = "dad_jokes"

    dad_joke_id: Mapped[int] = mapped_column(primary_key=True)
    joke: Mapped[str] = mapped_column(nullable=False)


class Deadline(Base):
    """A deadline for a university project"""

    __tablename__ = "deadlines"

    deadline_id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("ufora_courses.course_id"))
    name: Mapped[str] = mapped_column(nullable=False)
    deadline: Mapped[datetime] = mapped_column(nullable=False)

    course: Mapped[UforaCourse] = relationship(back_populates="deadlines", uselist=False, lazy="selectin")


class EasterEgg(Base):
    """An easter egg response"""

    __tablename__ = "easter_eggs"

    easter_egg_id: Mapped[int] = mapped_column(primary_key=True)
    match: Mapped[str] = mapped_column(nullable=False)
    response: Mapped[str] = mapped_column(nullable=False)
    exact: Mapped[bool] = mapped_column(nullable=False, server_default="1")
    startswith: Mapped[bool] = mapped_column(nullable=False, server_default="1")


class Event(Base):
    """A scheduled event"""

    __tablename__ = "events"

    event_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)
    notification_channel: Mapped[int] = mapped_column(BigInteger, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(nullable=False)


class FreeGame(Base):
    """A temporarily free game"""

    __tablename__ = "free_games"

    free_game_id: Mapped[int] = mapped_column(primary_key=True)


class GitHubLink(Base):
    """A user's GitHub link"""

    __tablename__ = "github_links"

    github_link_id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(nullable=False, unique=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"))

    user: Mapped[User] = relationship(back_populates="github_links", uselist=False, lazy="selectin")


class Jail(Base):
    """A user sitting in Didier Jail"""

    __tablename__ = "jail"

    jail_entry_i: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"))
    until: Mapped[datetime] = mapped_column(nullable=False)

    user: Mapped[User] = relationship(back_populates="jail", uselist=False, lazy="selectin")


class Link(Base):
    """Useful links that go useful places"""

    __tablename__ = "links"

    link_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    url: Mapped[str] = mapped_column(nullable=False)


class MemeTemplate(Base):
    """A meme template for the Imgflip API"""

    __tablename__ = "meme"

    meme_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    template_id: Mapped[int] = mapped_column(nullable=False, unique=True)
    field_count: Mapped[int] = mapped_column(nullable=False)


class NightlyData(Base):
    """Data for a user's Nightly stats"""

    __tablename__ = "nightly_data"

    nightly_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"))
    last_nightly: Mapped[Optional[date]] = mapped_column(nullable=True)
    count: Mapped[int] = mapped_column(server_default="0", nullable=False)

    user: Mapped[User] = relationship(back_populates="nightly_data", uselist=False, lazy="selectin")


class Reminder(Base):
    """Something that a user should be reminded of"""

    __tablename__ = "reminders"

    reminder_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"))
    category: Mapped[enums.ReminderCategory] = mapped_column(nullable=False)

    user: Mapped[User] = relationship(back_populates="reminders", uselist=False, lazy="selectin")


class Task(Base):
    """A Didier task"""

    __tablename__ = "tasks"

    task_id: Mapped[int] = mapped_column(primary_key=True)
    task: Mapped[enums.TaskType] = mapped_column(nullable=False, unique=True)
    previous_run: Mapped[datetime] = mapped_column(nullable=True)


class UforaCourse(Base):
    """A course on Ufora"""

    __tablename__ = "ufora_courses"

    course_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    code: Mapped[str] = mapped_column(nullable=False, unique=True)
    year: Mapped[int] = mapped_column(nullable=False)
    compulsory: Mapped[bool] = mapped_column(server_default="1", nullable=False)
    role_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True, unique=False)
    overarching_role_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True, unique=False)
    # This is not the greatest fix, but there can only ever be two, so it will do the job
    alternative_overarching_role_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True, unique=False)
    log_announcements: Mapped[bool] = mapped_column(server_default="0", nullable=False)

    announcements: Mapped[List[UforaAnnouncement]] = relationship(
        back_populates="course", cascade="all, delete-orphan", lazy="selectin"
    )
    aliases: Mapped[List[UforaCourseAlias]] = relationship(
        back_populates="course", cascade="all, delete-orphan", lazy="selectin"
    )
    deadlines: Mapped[List[Deadline]] = relationship(
        back_populates="course", cascade="all, delete-orphan", lazy="selectin"
    )


class UforaCourseAlias(Base):
    """An alias for a course on Ufora that we use to refer to them"""

    __tablename__ = "ufora_course_aliases"

    alias_id: Mapped[int] = mapped_column(primary_key=True)
    alias: Mapped[str] = mapped_column(nullable=False, unique=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("ufora_courses.course_id"))

    course: Mapped[UforaCourse] = relationship(back_populates="aliases", uselist=False, lazy="selectin")


class UforaAnnouncement(Base):
    """An announcement sent on Ufora"""

    __tablename__ = "ufora_announcements"

    announcement_id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("ufora_courses.course_id"))
    publication_date: Mapped[date] = mapped_column()

    course: Mapped[UforaCourse] = relationship(back_populates="announcements", uselist=False, lazy="selectin")


class User(Base):
    """A Didier user"""

    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    bank: Mapped[Bank] = relationship(
        back_populates="user", uselist=False, lazy="selectin", cascade="all, delete-orphan"
    )
    birthday: Mapped[Optional[Birthday]] = relationship(
        back_populates="user", uselist=False, lazy="selectin", cascade="all, delete-orphan"
    )
    bookmarks: Mapped[List[Bookmark]] = relationship(
        back_populates="user", uselist=True, lazy="selectin", cascade="all, delete-orphan"
    )
    command_stats: Mapped[List[CommandStats]] = relationship(
        back_populates="user", uselist=True, lazy="selectin", cascade="all, delete-orphan"
    )
    github_links: Mapped[List[GitHubLink]] = relationship(
        back_populates="user", uselist=True, lazy="selectin", cascade="all, delete-orphan"
    )
    jail: Mapped[Optional[Jail]] = relationship(
        back_populates="user", uselist=False, lazy="selectin", cascade="all, delete-orphan"
    )
    nightly_data: Mapped[NightlyData] = relationship(
        back_populates="user", uselist=False, lazy="selectin", cascade="all, delete-orphan"
    )
    reminders: Mapped[List[Reminder]] = relationship(
        back_populates="user", uselist=True, lazy="selectin", cascade="all, delete-orphan"
    )
    savings: Mapped[List[BankSavings]] = relationship(
        back_populates="user", uselist=False, lazy="selectin", cascade="all, delete-orphan"
    )
