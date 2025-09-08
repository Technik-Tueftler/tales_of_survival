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

class GameStatus(Enum):
    CREATED = 0
    RUNNING = 1
    PAUSED = 2
    STOPPED = 3
    FINISHED = 4
    FAILURE = 5

    _ICONS = {
        CREATED: "🆕",
        RUNNING: "🎮",
        PAUSED: "⏸️",
        STOPPED: "⏹️",
        FINISHED: "🏁",
        FAILURE: "❌",
    }

    @property
    def icon(self):
        return self._ICONS.get(self, "❓")


class INSPIRATIONALWORD(Base):
    __tablename__ = "inspirational_words"
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(nullable=False)
    chance: Mapped[int] = mapped_column(nullable=False)
    genre_id: Mapped[int] = mapped_column(ForeignKey("genres.id"))
    genres: Mapped["GENRE"] = relationship(back_populates="inspirational_words")

    def __repr__(self) -> str:
        return f"InspirationalWord(id={self.id}, text={self.text})"


class EVENT(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(nullable=False)
    chance: Mapped[int] = mapped_column(nullable=False)
    genre_id: Mapped[int] = mapped_column(ForeignKey("genres.id"))
    genres: Mapped["GENRE"] = relationship(back_populates="events")

    def __repr__(self) -> str:
        return f"Event(id={self.id}, text={self.text})"


class GENRE(Base):
    __tablename__ = "genres"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    storytelling_style: Mapped[str] = mapped_column(nullable=True)
    atmosphere: Mapped[str] = mapped_column(nullable=True)
    inspirational_words: Mapped[list["INSPIRATIONALWORD"]] = relationship()
    events: Mapped[list["EVENT"]] = relationship()

    def __repr__(self) -> str:
        return f"Genre(id={self.id}, name={self.name})"
