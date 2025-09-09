"""
File containing the database classes and general setups.
"""

import asyncio
from enum import Enum
from datetime import datetime
import environ
from sqlalchemy import Enum as AlchemyEnum
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine
from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy import ForeignKey
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


@environ.config(prefix="DB")
class DbConfiguration:
    """
    Configuration model for the database component.
    """

    db_url: str = environ.var("sqlite+aiosqlite:///files/TalesOfSurvival.db")


async def sync_db(engine: AsyncEngine):
    """
    Function to run the sync command and create all DB dependencies and tables

    Args:
        engine (AsyncEngine): The engine to run the sync command
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


class Base(DeclarativeBase):
    """Declarative base class

    Args:
        DeclarativeBase (_type_): Basic class that is inherited
    """

    __abdstract__ = True
    __allow_unmapped__ = True


class StoryType(Enum):
    EVENT = 0, "📣"
    FICTION = 1, "📕"

    def __init__(self, value, icon):
        self._value_ = value
        self.icon = icon


class GameStatus(Enum):
    """Enum for game status"""

    CREATED = 0, "🆕"
    RUNNING = 1, "🎮"
    PAUSED = 2, "⏸️"
    STOPPED = 3, "⏹️"
    FINISHED = 4, "🏁"
    FAILURE = 5, "⚠️"


class INSPIRATIONALWORD(Base):
    __tablename__ = "inspirational_words"
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(nullable=False)
    chance: Mapped[int] = mapped_column(nullable=False)
    genre_id: Mapped[int] = mapped_column(ForeignKey("genres.id"))  # 1:N
    genres: Mapped["GENRE"] = relationship(back_populates="inspirational_words")  # 1:N

    def __repr__(self) -> str:
        return f"InspirationalWord(id={self.id}, text={self.text})"


class EVENT(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(nullable=False)
    chance: Mapped[int] = mapped_column(nullable=False)
    genre_id: Mapped[int] = mapped_column(ForeignKey("genres.id"))  # 1:N
    genre: Mapped["GENRE"] = relationship(back_populates="events")  # 1:N

    def __repr__(self) -> str:
        return f"Event(id={self.id}, text={self.text})"


class GENRE(Base):
    __tablename__ = "genres"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    storytelling_style: Mapped[str] = mapped_column(nullable=True)
    atmosphere: Mapped[str] = mapped_column(nullable=True)
    inspirational_words: Mapped[list["INSPIRATIONALWORD"]] = relationship()  # 1:N
    events: Mapped[list["EVENT"]] = relationship()  # 1:N
    tale: Mapped["TALE"] = relationship(
        "TALE", back_populates="genre", uselist=False
    )  # 1:1

    def __repr__(self) -> str:
        return f"Genre(id={self.id}, name={self.name})"


class STORY(Base):
    __tablename__ = "storys"
    id: Mapped[int] = mapped_column(primary_key=True)
    request: Mapped[str] = mapped_column(nullable=True)
    response: Mapped[str] = mapped_column(nullable=True)
    summary: Mapped[str] = mapped_column(nullable=True)
    story_type = mapped_column(
        AlchemyEnum(StoryType, native_enum=False, validate_strings=True),
        default=StoryType.FICTION,
    )
    tale_id: Mapped[int] = mapped_column(ForeignKey("tales.id"))  # 1:N
    tale: Mapped["TALE"] = relationship(back_populates="storys")  # 1:N

    def __repr__(self) -> str:
        return f"Story(id={self.id}, type={self.story_type})"


class TALE(Base):
    __tablename__ = "tales"
    id: Mapped[int] = mapped_column(primary_key=True)
    language: Mapped[str] = mapped_column(nullable=False)
    genre_id: Mapped[int] = mapped_column(
        ForeignKey("genres.id"), nullable=False
    )  # 1:1
    genre: Mapped[GENRE] = relationship("GENRE", back_populates="tale", uselist=False)
    storys: Mapped[list["STORY"]] = relationship()  # 1:N
    game: Mapped["GAME"] = relationship(
        "GAME", back_populates="tale", uselist=False
    )  # 1:1

class GAME(Base):
    __tablename__ = "games"
    id: Mapped[int] = mapped_column(primary_key=True)
    game_name: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=True)
    status = mapped_column(
        AlchemyEnum(GameStatus, native_enum=False, validate_strings=True),
        default=GameStatus.CREATED,
    )
    start_date: Mapped[datetime] = mapped_column(nullable=False)
    end_date: Mapped[datetime] = mapped_column(nullable=True)
    message_id: Mapped[int] = mapped_column(nullable=False)
    channel_id: Mapped[int] = mapped_column(nullable=True)
    tale_id: Mapped[int] = mapped_column(
        ForeignKey("tales.id"), nullable=False
    )  # 1:1
    tale: Mapped[TALE] = relationship("TALE", back_populates="game", uselist=False)


class USER(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    dc_id: Mapped[str] = mapped_column(nullable=False)
