"""
This File contains the database setup, initialization functions and
general database related functions.
"""

from datetime import datetime
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.exc import SQLAlchemyError
from .db_classes import Base, INSPIRATIONALWORD, GENRE, EVENT
from .configuration import Configuration


async def test_db(config: Configuration):
    try:
        async with config.write_lock:
            async with config.session() as session:
                async with session.begin():
                    genre1 = GENRE(name="Action")
                    genre2 = GENRE(name="Adventure")
                    insp_word1 = INSPIRATIONALWORD(text="Courage", chance=0.5)
                    insp_word2 = INSPIRATIONALWORD(text="Wisdom", chance=0.5)
                    insp_word3 = INSPIRATIONALWORD(text="Strength", chance=0.5)
                    insp_word4 = INSPIRATIONALWORD(text="Honor", chance=0.5)
                    event1 = EVENT(text="A wild beast appears!", chance=0.7)
                    event2 = EVENT(text="You find a hidden treasure!", chance=0.3)
                    genre1.inspirational_words.extend(
                        [insp_word1, insp_word2, insp_word3]
                    )
                    genre2.inspirational_words.append(insp_word4)
                    genre1.events.append(event1)
                    genre2.events.append(event2)
                    session.add_all([genre1, genre2])
                    # await session.refresh(genre1)
                    # tale = TALE(language="deutsch", genre=genre1)
                    # session.add(tale)

    except Exception as e:
        print(e)


async def get_genre_f_name(config: Configuration, genre_name: str) -> GENRE | None:
    """
    This function retrieves the last GENRE object from the database based on the
    provided genre name. The reason for returning the last entry is to manage
    adaptions to genre over time, ensuring that without deleting old versions in
    case of traceability to old games.

    Args:
        config (Configuration): Programm configuration
        genre_name (str): Genre name to search for

    Returns:
        GENRE | None: Found last genre with loaded inspirational words and events or None
    """
    try:
        config.logger.trace(f"Entering function with argument: {genre_name}")
        async with config.session() as session:
            async with session.begin():
                genres = (
                    (
                        await session.execute(
                            select(GENRE)
                            .where(GENRE.name == genre_name)
                            .options(selectinload(GENRE.inspirational_words))
                            .options(selectinload(GENRE.events))
                        )
                    )
                    .scalars()
                    .all()
                )
                if not genres:
                    config.logger.debug("No genre found and return None")
                    return None
                return genres[-1]
    except (AttributeError, SQLAlchemyError, TypeError) as err:
        config.logger.error(f"Error in sql select: {err}")
        return None
