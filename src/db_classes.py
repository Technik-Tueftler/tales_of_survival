"""
File containing the database classes and general setups.
"""
import asyncio
import environ
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine
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


class Player(Base):
    __tablename__ = "players"
    id: Mapped[int] = mapped_column(primary_key=True)
    alive: Mapped[bool] = mapped_column(default=True)
    character_id: Mapped[str] = mapped_column(ForeignKey("characters.id"), unique=True)

    character: Mapped["Character"] = relationship(back_populates="player", uselist=False)


class Character(Base):
    __tablename__ = "characters"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    age: Mapped[int] = mapped_column()
    background: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    pos_trait: Mapped[str] = mapped_column()
    neg_trait: Mapped[str] = mapped_column()
    summary: Mapped[str] = mapped_column()

    player: Mapped["Player"] = relationship(back_populates="character", uselist=False)
