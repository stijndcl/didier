from __future__ import annotations

from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class UforaCourse(Base):
    """A course on Ufora"""

    __tablename__ = "ufora_courses"

    course_id: int = Column(Integer, primary_key=True)
    name: str = Column(Text, nullable=False, unique=True)
    code: str = Column(Text, nullable=False, unique=True)
    year: int = Column(Integer, nullable=False)

    announcements: list[UforaAnnouncement] = relationship(
        "UforaAnnouncement", back_populates="course", cascade="all, delete-orphan"
    )
    aliases: list[UforaCourseAlias] = relationship(
        "UforaCourseAlias", back_populates="course", cascade="all, delete-orphan"
    )


class UforaCourseAlias(Base):
    """An alias for a course on Ufora that we use to refer to them"""

    __tablename__ = "ufora_course_aliases"

    alias_id: int = Column(Integer, primary_key=True)
    alias: str = Column(Text, nullable=False, unique=True)
    course_id: int = Column(Integer, ForeignKey("ufora_courses.course_id"))

    course: UforaCourse = relationship("UforaCourse", back_populates="aliases", uselist=False)


class UforaAnnouncement(Base):
    """An announcement sent on Ufora"""

    __tablename__ = "ufora_announcements"

    announcement_id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("ufora_courses.course_id"))

    course = relationship("UforaCourse", back_populates="announcements", uselist=False)
