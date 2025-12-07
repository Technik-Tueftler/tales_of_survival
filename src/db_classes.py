"""
File containing the database classes and general setups.
"""

from enum import Enum
from datetime import datetime, timezone
import environ
from sqlalchemy import Enum as AlchemyEnum
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import ForeignKey, String, BigInteger
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
    INIT = 0, "🛠️", "init"
    EVENT = 1, "📣", "event"
    FICTION = 2, "📕", "fiction"

    def __init__(self, value, icon, text):
        self._value_ = value
        self.icon = icon
        self.text = text


class StartCondition(Enum):
    """
    Enum to define type of start condition and map an emoji.
    """
    S_ZOMBIE = 0, "🧟‍♀️", "Standard zombie tale"
    OWN = 1, "✍️", "Your own prompt"

    def __init__(self, value, icon, text):
        self._value_ = value
        self.icon = icon
        self.text = text


class GameStatus(Enum):
    """
    Enum to define status of game and map an emoji.
    """

    CREATED = 0, "🆕", "created"
    RUNNING = 1, "🎮", "running"
    PAUSED = 2, "⏸️", "paused"
    STOPPED = 3, "⏹️", "stopped"
    FINISHED = 4, "🏁", "finished"
    FAILURE = 5, "⚠️", "failure"

    def __new__(cls, value, icon="", lable=""):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.icon = icon
        obj.lable = lable
        return obj


class INSPIRATIONALWORD(Base):
    """
    Class definition for inspirational words. These are used to
    generate random words for the story for a genre.
    """

    __tablename__ = "inspirational_words"
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(String(1000), nullable=False)
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
    text: Mapped[str] = mapped_column(String(2000), nullable=False)
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
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    storytelling_style: Mapped[str] = mapped_column(String(100), nullable=True)
    atmosphere: Mapped[str] = mapped_column(String(100), nullable=True)
    language: Mapped[str] = mapped_column(String(100), nullable=False)
    active: Mapped[bool] = mapped_column(default=True)
    inspirational_words: Mapped[list["INSPIRATIONALWORD"]] = relationship()  # 1:N
    events: Mapped[list["EVENT"]] = relationship()  # 1:N
    tales: Mapped[list["TALE"]] = relationship("TALE", back_populates="genre") # 1:N

    def __repr__(self) -> str:
        return f"Genre(id={self.id}, name={self.name})"


class STORY(Base):
    """
    Class definition for story in which individual story parts are managed. These are then made
    available as a history for creating new stories elements.
    """

    __tablename__ = "stories"
    id: Mapped[int] = mapped_column(primary_key=True)
    request: Mapped[str] = mapped_column(String(2000), nullable=True)
    response: Mapped[str] = mapped_column(String(2000), nullable=True)
    summary: Mapped[str] = mapped_column(String(2000), nullable=True)
    story_type = mapped_column(
        AlchemyEnum(StoryType, native_enum=False, validate_strings=True),
        default=StoryType.FICTION,
    )
    timestamp: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    messages: Mapped[list["MESSAGE"]] = relationship()  # 1:N
    tale_id: Mapped[int] = mapped_column(ForeignKey("tales.id"))  # 1:N
    tale: Mapped["TALE"] = relationship(back_populates="stories")  # 1:N

    def __repr__(self) -> str:
        return f"Story(id={self.id}, type={self.story_type})"


class MESSAGE(Base):
    """
    Class definition for messages that send to Discord channel for a story.
    """
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    message_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    story_id: Mapped[int] = mapped_column(ForeignKey("stories.id"))  # 1:N
    story: Mapped["STORY"] = relationship(back_populates="messages")  # 1:N


class TALE(Base):
    """
    Class definition for tale in which the complete story is defined.
    """

    __tablename__ = "tales"
    id: Mapped[int] = mapped_column(primary_key=True)
    genre_id: Mapped[int] = mapped_column(ForeignKey("genres.id"), nullable=False)
    genre: Mapped[GENRE] = relationship("GENRE", back_populates="tales") # 1:1
    stories: Mapped[list["STORY"]] = relationship()  # 1:N
    game: Mapped["GAME"] = relationship("GAME", back_populates="tale", uselist=False)

    def __repr__(self) -> str:
        return f"Tale(id={self.id}, genre_id={self.genre_id}, game={self.game.name})"


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
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    status = mapped_column(
        AlchemyEnum(GameStatus, native_enum=False, validate_strings=True),
        default=GameStatus.CREATED,
    )
    start_date: Mapped[datetime] = mapped_column(nullable=False)
    end_date: Mapped[datetime] = mapped_column(nullable=True)
    message_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    channel_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    tale_id: Mapped[int] = mapped_column(ForeignKey("tales.id"), nullable=False)  # 1:1
    tale: Mapped[TALE] = relationship("TALE", back_populates="game", uselist=False)
    user_participations: Mapped[list["UserGameCharacterAssociation"]] = relationship(
        back_populates="game"
    ) # N:M

    def __repr__(self) -> str:
        return f"Game(id={self.id}, name={self.name})"

class USER(Base):
    """
    Class definition for user to manage all user based informations.
    """

    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    dc_id: Mapped[str] = mapped_column(String(100), nullable=False)
    characters: Mapped[list["CHARACTER"]] = relationship(back_populates="user")
    game_participations: Mapped[list["UserGameCharacterAssociation"]] = relationship(
        back_populates="user"
    ) # N:M


class CHARACTER(Base):
    """
    Class definition for playable characters.
    """

    __tablename__ = "characters"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    age: Mapped[int] = mapped_column(nullable=False)
    background: Mapped[str] = mapped_column(String(2000), nullable=False)
    description: Mapped[str] = mapped_column(String(2000), nullable=False)
    pos_trait: Mapped[str] = mapped_column(String(2000), nullable=True)
    neg_trait: Mapped[str] = mapped_column(String(2000), nullable=True)
    summary: Mapped[str] = mapped_column(String(2000), nullable=False)
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
