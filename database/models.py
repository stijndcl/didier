from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Column, Integer, Text, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Bank(Base):
    """A user's currency information"""

    __tablename__ = "bank"

    bank_id: int = Column(Integer, primary_key=True)
    user_id: int = Column(BigInteger, ForeignKey("users.user_id"))

    dinks: int = Column(BigInteger, default=0, nullable=False)

    # Interest rate
    interest_level: int = Column(Integer, default=1, nullable=False)

    # Maximum amount that can be stored in the bank
    capacity_level: int = Column(Integer, default=1, nullable=False)

    # Maximum amount that can be robbed
    rob_level: int = Column(Integer, default=1, nullable=False)

    user: User = relationship("User", uselist=False, back_populates="bank", lazy="selectin")


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


class NightlyData(Base):
    """Data for a user's Nightly stats"""

    __tablename__ = "nightly_data"

    nightly_id: int = Column(Integer, primary_key=True)
    user_id: int = Column(BigInteger, ForeignKey("users.user_id"))
    last_nightly: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)
    count: int = Column(Integer, default=0, nullable=False)

    user: User = relationship("User", back_populates="nightly_data", uselist=False, lazy="selectin")


class UforaCourse(Base):
    """A course on Ufora"""

    __tablename__ = "ufora_courses"

    course_id: int = Column(Integer, primary_key=True)
    name: str = Column(Text, nullable=False, unique=True)
    code: str = Column(Text, nullable=False, unique=True)
    year: int = Column(Integer, nullable=False)
    log_announcements: bool = Column(Boolean, default=False, nullable=False)

    announcements: list[UforaAnnouncement] = relationship(
        "UforaAnnouncement", back_populates="course", cascade="all, delete-orphan", lazy="selectin"
    )
    aliases: list[UforaCourseAlias] = relationship(
        "UforaCourseAlias", back_populates="course", cascade="all, delete-orphan", lazy="selectin"
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
    publication_date: datetime = Column(DateTime(timezone=True))

    course: UforaCourse = relationship("UforaCourse", back_populates="announcements", uselist=False, lazy="selectin")


class User(Base):
    """A Didier user"""

    __tablename__ = "users"

    user_id: int = Column(BigInteger, primary_key=True)

    bank: Bank = relationship(
        "Bank", back_populates="user", uselist=False, lazy="selectin", cascade="all, delete-orphan"
    )
    nightly_data: NightlyData = relationship(
        "NightlyData", back_populates="user", uselist=False, lazy="selectin", cascade="all, delete-orphan"
    )
