"""
File containing the database classes and general setups.
"""

from enum import Enum
from datetime import datetime, timezone
import environ
from sqlalchemy import Enum as AlchemyEnum
from sqlalchemy.ext.asyncio import AsyncEngine
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
    """
    Enum to define type of story and map an emoji.
    """

    EVENT = 0, "📣", "event"
    FICTION = 1, "📕", "fiction"

    def __init__(self, value, icon, text):
        self._value_ = value
        self.icon = icon
        self.text = text


class GameStatus(Enum):
    """
    Enum to define status of game and map an emoji.
    """

    CREATED = 0, "🆕"
    RUNNING = 1, "🎮"
    PAUSED = 2, "⏸️"
    STOPPED = 3, "⏹️"
    FINISHED = 4, "🏁"
    FAILURE = 5, "⚠️"

    def __init__(self, value, icon):
        self._value_ = value
        self.icon = icon


class INSPIRATIONALWORD(Base):
    """
    Class definition for inspirational words. These are used to
    generate random words for the story for a genre.
    """

    __tablename__ = "inspirational_words"
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(nullable=False)
    chance: Mapped[int] = mapped_column(nullable=False)
    genre_id: Mapped[int] = mapped_column(ForeignKey("genres.id"))  # 1:N
    genres: Mapped["GENRE"] = relationship(back_populates="inspirational_words")  # 1:N

    def __repr__(self) -> str:
        return f"InspirationalWord(id={self.id}, text={self.text})"


class EVENT(Base):
    """
    Class definition for fixed events that can occur in a genre.
    """

    __tablename__ = "events"
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(nullable=False)
    chance: Mapped[int] = mapped_column(nullable=False)
    genre_id: Mapped[int] = mapped_column(ForeignKey("genres.id"))  # 1:N
    genre: Mapped["GENRE"] = relationship(back_populates="events")  # 1:N

    def __repr__(self) -> str:
        return f"Event(id={self.id}, text={self.text})"


class GENRE(Base):
    """
    Class definition for genre for central definition to
    determine the general story creation.
    """

    __tablename__ = "genres"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    storytelling_style: Mapped[str] = mapped_column(nullable=True)
    atmosphere: Mapped[str] = mapped_column(nullable=True)
    language: Mapped[str] = mapped_column(nullable=False)
    inspirational_words: Mapped[list["INSPIRATIONALWORD"]] = relationship()  # 1:N
    events: Mapped[list["EVENT"]] = relationship()  # 1:N
    # tale: Mapped["TALE"] = relationship(
    #     "TALE", back_populates="genre", uselist=False
    # )  # 1:1
    tales: Mapped[list["TALE"]] = relationship("TALE", back_populates="genre")

    def __repr__(self) -> str:
        return f"Genre(id={self.id}, name={self.name})"


class STORY(Base):
    """
    Class definition for story in which individual story parts are managed. These are then made
    available as a history for creating new stories elements.
    """

    __tablename__ = "stories"
    id: Mapped[int] = mapped_column(primary_key=True)
    request: Mapped[str] = mapped_column(nullable=True)
    response: Mapped[str] = mapped_column(nullable=True)
    summary: Mapped[str] = mapped_column(nullable=True)
    story_type = mapped_column(
        AlchemyEnum(StoryType, native_enum=False, validate_strings=True),
        default=StoryType.FICTION,
    )
    tale_id: Mapped[int] = mapped_column(ForeignKey("tales.id"))  # 1:N
    tale: Mapped["TALE"] = relationship(back_populates="stories")  # 1:N

    def __repr__(self) -> str:
        return f"Story(id={self.id}, type={self.story_type})"


class TALE(Base):
    """
    Class definition for tale in which the complete story is defined.
    """

    __tablename__ = "tales"
    id: Mapped[int] = mapped_column(primary_key=True)
    genre_id: Mapped[int] = mapped_column(ForeignKey("genres.id"), nullable=False)
    # genre: Mapped[GENRE] = relationship("GENRE", back_populates="tale", uselist=False) # 1:1
    genre: Mapped[GENRE] = relationship("GENRE", back_populates="tales")

    stories: Mapped[list["STORY"]] = relationship()  # 1:N
    game: Mapped["GAME"] = relationship("GAME", back_populates="tale", uselist=False)


class UserGameCharacterAssociation(Base):
    """
    Association table to link users, games, and characters in a many-to-many relationship.
    One User can participate in many Games with many Characters
    One Game can have many Users participating with many Characters
    """

    __tablename__ = "association_user_game_character"
    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    character_id: Mapped[int] = mapped_column(
        ForeignKey("characters.id"), nullable=True
    )
    request_date: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    end_date: Mapped[datetime] = mapped_column(nullable=True)

    game: Mapped["GAME"] = relationship("GAME", back_populates="user_participations")
    user: Mapped["USER"] = relationship("USER", back_populates="game_participations")
    character: Mapped["CHARACTER"] = relationship(
        "CHARACTER", back_populates="game_assignments"
    )


class GAME(Base):
    """
    Class definition for game to store general game informations.
    """

    __tablename__ = "games"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    status = mapped_column(
        AlchemyEnum(GameStatus, native_enum=False, validate_strings=True),
        default=GameStatus.CREATED,
    )
    start_date: Mapped[datetime] = mapped_column(nullable=False)
    end_date: Mapped[datetime] = mapped_column(nullable=True)
    message_id: Mapped[int] = mapped_column(nullable=True)
    channel_id: Mapped[int] = mapped_column(nullable=True)
    tale_id: Mapped[int] = mapped_column(ForeignKey("tales.id"), nullable=False)  # 1:1
    tale: Mapped[TALE] = relationship("TALE", back_populates="game", uselist=False)
    # M:N - Association mit Back_populates
    # users: Mapped[list["USER"]] = relationship(
    #     secondary=association_user_game, back_populates="games"
    # )
    user_participations: Mapped[list["UserGameCharacterAssociation"]] = relationship(
        back_populates="game"
    )


class USER(Base):
    """
    Class definition for user to manage all user based informations.
    """

    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    dc_id: Mapped[str] = mapped_column(nullable=False)
    characters: Mapped[list["CHARACTER"]] = relationship(back_populates="user")
    game_participations: Mapped[list["UserGameCharacterAssociation"]] = relationship(
        back_populates="user"
    )


class CHARACTER(Base):
    """
    Class definition for playable characters.
    """

    __tablename__ = "characters"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    age: Mapped[int] = mapped_column(nullable=False)
    background: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    pos_trait: Mapped[str] = mapped_column(nullable=True)
    neg_trait: Mapped[str] = mapped_column(nullable=True)
    summary: Mapped[str] = mapped_column(nullable=False)
    alive: Mapped[bool] = mapped_column(default=True)
    start_date: Mapped[datetime] = mapped_column(nullable=True)
    end_date: Mapped[datetime] = mapped_column(nullable=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    user: Mapped["USER"] = relationship(back_populates="characters")

    game_assignments: Mapped[list["UserGameCharacterAssociation"]] = relationship(
        back_populates="character"
    )

    def __repr__(self) -> str:
        return f"Character(id={self.id}, name={self.name})"
