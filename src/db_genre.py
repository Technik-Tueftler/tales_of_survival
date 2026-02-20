"""
This module contains all functions which contains database interactions for the genre.
"""

import sys

from sqlalchemy import select, exists
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import selectinload

from .configuration import Configuration
from .db_classes import (
    EVENT,
    GENRE,
    INSPIRATIONALWORD,
)
from .db import ImportResult

async def get_unique_genre_from_content(
    config: Configuration, genre: dict
) -> GENRE | None:
    """
    Function to get a unique genre based on the content of the genre.

    Args:
        config (Configuration): App configuration
        genre (dict): Genre content

    Returns:
        GENRE | None: Found genre or None in case of not found
    """
    try:
        async with config.session() as session, session.begin():
            statement = (
                select(GENRE)
                .where(GENRE.name == genre["name"])
                .where(GENRE.storytelling_style == genre["storytelling-type"])
                .where(GENRE.atmosphere == genre["atmosphere"])
                .where(GENRE.language == genre["language"])
                .options(selectinload(GENRE.inspirational_words))
                .options(selectinload(GENRE.events))
            )
            return (await session.execute(statement)).scalar_one_or_none()

    except (AttributeError, SQLAlchemyError, TypeError):
        config.logger.opt(exception=sys.exc_info()).error("Error in sql select.")
        return None

async def get_genre_double_cond(
    config: Configuration, genre_id: int, genre_name: str = None
) -> GENRE | None:
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
        config.logger.trace(f"Entering function with argument: {genre_id, genre_name}")
        async with config.session() as session, session.begin():
            if genre_name:
                filter_stmt = GENRE.name == genre_name
            else:
                filter_stmt = GENRE.id == genre_id
            genres = (
                (
                    await session.execute(
                        select(GENRE)
                        .where(filter_stmt)
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
            config.logger.debug(
                f"Found genre with ID {genres[-1].id} annd name {genres[-1].name}"
            )
            return genres[-1]
    except (AttributeError, SQLAlchemyError, TypeError):
        config.logger.opt(exception=sys.exc_info()).error("Error in sql select")
        return None


async def check_exist_unique_genre(config: Configuration, genre: dict) -> bool:
    """
    Function checks whether the genre passed is unique.

    Args:
        config (Configuration): App configuration
        genre (dict): New genre from yml load

    Returns:
        bool: Transferred genre already exists.
    """
    try:
        async with config.session() as session, session.begin():
            statement = select(
                exists()
                .where(GENRE.name == genre["name"])
                .where(GENRE.storytelling_style == genre["storytelling-type"])
                .where(GENRE.atmosphere == genre["atmosphere"])
                .where(GENRE.language == genre["language"])
            )
            return (await session.execute(statement)).scalar()
    except (AttributeError, SQLAlchemyError, TypeError):
        config.logger.opt(exception=sys.exc_info()).error("Error in sql select.")
        return False


async def create_genre_from_input(config: Configuration, result: ImportResult):
    """
    Function to create genre from imported file.

    Args:
        config (Configuration): App configuration
        result (ImportResult): Result class from importing a file
    """
    try:
        final_genre = []
        missed_genre = []
        for genre in result.data:
            if await check_exist_unique_genre(config, genre):
                config.logger.debug(
                    f"The following genre already exist: {genre["name"]}"
                )
                missed_genre.append(genre["name"])
                continue
            temp_genre = GENRE(
                name=genre["name"],
                storytelling_style=genre["storytelling-type"],
                atmosphere=genre["atmosphere"],
                language=genre["language"],
            )
            for insp_word in genre.get("inspirational-words", []):
                temp_genre.inspirational_words.extend(
                    INSPIRATIONALWORD(text=word, chance=insp_word["chance"])
                    for word in insp_word["words"]
                )
            for events in genre.get("events", []):
                temp_genre.events.extend(
                    EVENT(text=event, chance=events["chance"])
                    for event in events["event"]
                )
            final_genre.append(temp_genre)
        async with config.write_lock, config.session() as session, session.begin():
            session.add_all(final_genre)
        result.import_number = len(final_genre)
        result.success = True
        if missed_genre:
            result.text_genre = (
                "The following genres already exist with the settings "
                + f"provided: {", ".join(missed_genre)}. "
            )
    except (KeyError, IntegrityError):
        config.logger.opt(exception=sys.exc_info()).error(
            "Error while import genre file."
        )


async def get_loaded_genre_from_id(
    config: Configuration, genre_id: int
) -> GENRE | None:
    """
    This function returns the genre object with the passed ID. If the ID 
    does not exist, None is returned.

    Args:
        config (Configuration): App configuration
        genre_id (int): Genre ID to load object

    Returns:
        GENRE | None: Found genre or NONE
    """
    try:
        async with config.session() as session, session.begin():
            statement = (
                select(GENRE)
                .where(GENRE.id == genre_id)
                .options(selectinload(GENRE.inspirational_words))
                .options(selectinload(GENRE.events))
            )
            return (await session.execute(statement)).scalar_one_or_none()

    except (AttributeError, SQLAlchemyError, TypeError):
        config.logger.opt(exception=sys.exc_info()).error("Error in sql select.")
        return None


async def get_all_active_genre(config: Configuration) -> list[GENRE]:
    """
    Function to get all genres from the database.

    Args:
        config (Configuration): App configuration

    Returns:
        list[GENRE]: List of all genres in the database
    """
    async with config.session() as session, session.begin():
        return (
            (await session.execute(select(GENRE).where(GENRE.active.is_(True))))
            .scalars()
            .all()
        )


async def get_active_genre(config: Configuration) -> list[GENRE]:
    """
    This function retrieves all active genres from the database.

    Args:
        config (Configuration): App configuration

    Returns:
        list[GENRE]: List with all active genres
    """
    try:
        async with config.session() as session, session.begin():
            statement = select(GENRE).where(GENRE.active.is_(True))
            return (await session.execute(statement)).scalars().all()
    except (AttributeError, SQLAlchemyError, TypeError):
        config.logger.opt(exception=sys.exc_info()).error("Error in sql select.")
        return []


async def deactivate_genre_with_id(config: Configuration, genre_id: int) -> None:
    """
    This function deactivates a genre based on the handed over genre id.

    Args:
        config (Configuration): App configuration
        genre_id (int): Genre id to deactivate
    """
    try:
        async with config.session() as session, session.begin():
            statement = select(GENRE).where(GENRE.id == genre_id)
            genre = (await session.execute(statement)).scalar_one_or_none()
            if genre:
                genre.active = False
                config.logger.debug(f"Deactivated genre with ID: {genre_id}")
    except (AttributeError, SQLAlchemyError, TypeError):
        config.logger.opt(exception=sys.exc_info()).error("Error in sql select.")


async def get_inactive_genre(config: Configuration) -> list[GENRE]:
    """
    This function retrieves all inactive genres from the database.

    Args:
        config (Configuration): App configuration

    Returns:
        list[GENRE]: List with all inactive genres
    """
    try:
        async with config.session() as session, session.begin():
            statement = select(GENRE).where(GENRE.active.is_(False))
            return (await session.execute(statement)).scalars().all()
    except (AttributeError, SQLAlchemyError, TypeError):
        config.logger.opt(exception=sys.exc_info()).error("Error in sql select.")
        return []


async def activate_genre_with_id(config: Configuration, genre_id: int) -> None:
    """
    This function activates a genre based on the handed over genre id.

    Args:
        config (Configuration): App configuration
        genre_id (int): Genre id to activate
    """
    try:
        async with config.session() as session, session.begin():
            statement = select(GENRE).where(GENRE.id == genre_id)
            genre = (await session.execute(statement)).scalar_one_or_none()
            if genre:
                genre.active = True
                config.logger.debug(f"Deactivated genre with ID: {genre_id}")
    except (AttributeError, SQLAlchemyError, TypeError):
        config.logger.opt(exception=sys.exc_info()).error("Error in sql select.")
