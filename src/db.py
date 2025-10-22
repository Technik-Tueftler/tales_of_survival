"""
This File contains the database setup, initialization functions and
general database related functions.
"""

from dataclasses import dataclass

import discord
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import selectinload, joinedload

from .configuration import Configuration, ProcessInput
from .db_classes import (
    CHARACTER,
    EVENT,
    GAME,
    GENRE,
    INSPIRATIONALWORD,
    TALE,
    USER,
    UserGameCharacterAssociation,
    GameStatus,
    STORY
)


@dataclass
class ImportResult:
    """
    Result class from importing a file.
    """

    file_path: str
    data: dict
    success: bool = False
    import_number: int = 0


# async def test_db4(config: Configuration):
#     """
#     Test
#     """
#     print(20 * "#" + " Start Test 4 " + 20 * "#")
#     async with config.session() as session:
#         async with session.begin():
#             tale = (
#                 await session.execute(
#                     select(TALE).where(TALE.id == 2).options(selectinload(TALE.stories))
#                 )
#             ).scalar_one_or_none()
#     for story in tale.stories:
#         print(story.id, story.story_type.icon)
# async def test_db2(config: Configuration):
#     """
#     Test
#     """
#     print(20 * "#" + " Start Test 2 " + 20 * "#")
#     async with config.write_lock:
#         async with config.session() as session:
#             async with session.begin():
#                 genre1 = GENRE(name="Action", language="deutsch")
#                 event1 = EVENT(text="lala blub blub", chance=0.6, genre=genre1)
#                 event2 = EVENT(text="lala blub blub 2", chance=0.6, genre=genre1)
#                 session.add_all([event1, event2])
#     async with config.session() as session:
#         # stmt = select(EVENT).join(EVENT.genre).filter(GENRE.name == "Action")
#         stmt = (
#             select(EVENT)
#             .join(EVENT.genre)
#             .where(GENRE.name == "Action")
#             .options(selectinload(EVENT.genre))
#         )
#         events = (await session.execute(stmt)).scalars().all()
#         for event in events:
#             print(event, event.genre.id)


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
    except (AttributeError, SQLAlchemyError, TypeError) as err:
        config.logger.error(f"Error in sql select: {err}")
        return None


async def create_genre_from_input(config: Configuration, result: ImportResult):
    """
    Function to create genre from imported file.

    Args:
        config (Configuration): App configuration
        result (ImportResult): Result class from importing a file
    """
    try:
        final_genre = []
        for genre in result.data:
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
    except (KeyError, IntegrityError) as err:
        config.logger.error(f"Error while import genre file: {err}")


async def create_character_from_input(config: Configuration, result: ImportResult):
    """
    Function to create character from imported file.

    Args:
        config (Configuration): App configuration
        result (ImportResult): Result class from importing a file
    """
    try:
        async with config.write_lock, config.session() as session, session.begin():
            final_character = [
                CHARACTER(
                    name=character["name"],
                    age=character["age"],
                    background=character["background"],
                    description=character["description"],
                    pos_trait=character["pos_trait"],
                    neg_trait=character["neg_trait"],
                    summary=character["summary"],
                )
                for character in result.data
            ]
            session.add_all(final_character)
        result.import_number = len(final_character)
        result.success = True
    except (KeyError, IntegrityError) as err:
        config.logger.error(f"Error while import character file: {err}")


async def get_characters_from_ids(
    config: Configuration, ids: list[int]
) -> list[CHARACTER]:
    """
    Function to get characters from a list of ids.

    Args:
        config (Configuration): App configuration
        ids (list[int]): List with all character ids

    Returns:
        list[CHARACTER]: List of characters
    """
    async with config.session() as session, session.begin():
        return (
            (await session.execute(select(CHARACTER).where(CHARACTER.id.in_(ids))))
            .scalars()
            .all()
        )


async def get_object_by_id(
    config: Configuration,
    obj_type: UserGameCharacterAssociation | CHARACTER | GAME,
    obj_id: int,
) -> UserGameCharacterAssociation | CHARACTER | None:
    """
    Function to get a object from the database by its id.

    Args:
        config (Configuration): App configuration
        obj_type (UserGameCharacterAssociation): Type of the object to get
        obj_id (int): Id of the object to get
    """
    async with config.session() as session, session.begin():
        return (
            await session.execute(select(obj_type).where(obj_type.id == obj_id))
        ).scalar_one_or_none()


async def get_all_genre(config: Configuration) -> list[GENRE]:
    """
    Function to get all genres from the database.

    Args:
        config (Configuration): App configuration

    Returns:
        list[GENRE]: List of all genres in the database
    """
    async with config.session() as session, session.begin():
        return (await session.execute(select(GENRE))).scalars().all()


async def process_player(
    config: Configuration, user_list: list[discord.member.Member]
) -> list[USER]:
    """
    Function to process a user list and add them to the database if they are not already there.

    Args:
        config (Configuration): App configuration
        user_list (list[discord.member.Member]): List of users to process

    Returns:
        list[User]: processed user list
    """
    processed_user_list = []
    async with config.write_lock, config.session() as session, session.begin():
        for user in user_list:
            temp_user = (
                await session.execute(select(USER).filter(USER.dc_id == user.id))
            ).scalar_one_or_none()
            if temp_user is None:
                temp_user = USER(name=user.name, dc_id=user.id)
                session.add(temp_user)
                config.logger.debug(f"User {temp_user.name} added to the database.")
            processed_user_list.append(temp_user)
    return processed_user_list


async def update_db_objs(
    config: Configuration,
    objs: list[GAME | USER | TALE | GENRE, STORY],
) -> None:
    """
    Function to update a game or player object in the database

    Args:
        config (Configuration): App configuration
        obj (GAME | USER | TALE | GENRE): Object to update in the database
    """
    try:
        async with config.write_lock, config.session() as session, session.begin():
            session.add_all(objs)
            await session.flush()
            for obj in objs:
                config.logger.trace(
                    f"Updated object in database: {obj.__class__.__name__} with ID: {obj.id}"
                )
    except Exception as err:
        print(err, type(err))


async def get_available_characters(config: Configuration) -> list[CHARACTER]:
    """
    Function to get all characters from the database which are not assigned to a user.

    Args:
        config (Configuration): App configuration
    """
    try:
        async with config.session() as session, session.begin():
            statement = (
                select(CHARACTER)
                .where(CHARACTER.alive.is_(True))
                .where(CHARACTER.user_id.is_(None))
            )
            result = (await session.execute(statement)).scalars().all()

            if result is None or len(result) == 0:
                config.logger.debug("No available characters found in the database")
                return
            return result

    except (AttributeError, SQLAlchemyError, TypeError) as err:
        config.logger.error(f"Error in sql select: {err}")
        return


async def get_all_user_games(config: Configuration, process_data: ProcessInput) -> None:
    try:
        async with config.session() as session, session.begin():
            statement = (
                select(GAME)
                .join(GAME.user_participations)
                .join(UserGameCharacterAssociation.user)
                .where(USER.dc_id == process_data.user_dc_id)
                .where(UserGameCharacterAssociation.character_id.is_(None))
                .where(UserGameCharacterAssociation.end_date.is_(None))
            )
            process_data.available_games = (
                (await session.execute(statement)).scalars().all()
            )

    except (AttributeError, SQLAlchemyError, TypeError) as err:
        config.logger.error(f"Error in sql select: {err}")
        return


async def get_all_games(config: Configuration, process_data: ProcessInput) -> None:
    """
    Function to get all available games from the database which are not finished.

    Args:
        config (Configuration): App configuration
        request_data (dict):
    """
    try:
        async with config.session() as session, session.begin():
            statement = select(GAME).where(GAME.end_date.is_(None))
            result = (await session.execute(statement)).scalars().all()

            if result is None or len(result) == 0:
                config.logger.debug("No available games found in the database")
                return
            process_data.available_games = result

    except (AttributeError, SQLAlchemyError, TypeError) as err:
        config.logger.error(f"Error in sql select: {err}")
        return


async def get_tale_from_game_id(config: Configuration, game_id: int) -> TALE | None:
    try:
        async with config.session() as session, session.begin():
            statement = (
                select(TALE)
                .join(TALE.game)
                .options(
                    joinedload(TALE.genre).options(selectinload(GENRE.events)),
                    joinedload(TALE.game),
                )
                .where(GAME.id == game_id)
            )
            return (await session.execute(statement)).scalar_one_or_none()

    except (AttributeError, SQLAlchemyError, TypeError) as err:
        config.logger.error(f"Error in sql select: {err}")
        return


async def get_games_w_status(
    config: Configuration, status: list[GameStatus]
) -> list[GAME]:
    """
    This function get all changeable games back. Games that have the status
    CREATED, RUNNING or PAUSED can be changed.

    Args:
        config (Configuration): App configuration

    Returns:
        list[Game]: The list if changeable games
    """
    config.logger.trace(f"Called with status: {status}")
    async with config.session() as session, session.begin():
        games = (
            (await session.execute(select(GAME).where(GAME.status.in_(status))))
            .scalars()
            .all()
        )
    return games


async def get_user_from_dc_id(config: Configuration, dc_id: str) -> USER:
    try:
        async with config.session() as session, session.begin():
            statement = (
                select(USER)
                .where(USER.dc_id == dc_id)
            )
            return (await session.execute(statement)).scalar_one_or_none()

    except (AttributeError, SQLAlchemyError, TypeError) as err:
        config.logger.error(f"Error in sql select: {err}")
        return


async def get_mapped_ugc_association(
    config: Configuration, game_id: int, user_id
) -> UserGameCharacterAssociation:
    try:
        async with config.session() as session, session.begin():
            statement = (
                select(UserGameCharacterAssociation)
                .where(UserGameCharacterAssociation.game_id == game_id)
                .where(UserGameCharacterAssociation.user_id == user_id)
            )
            return (await session.execute(statement)).scalar_one_or_none()

    except (AttributeError, SQLAlchemyError, TypeError) as err:
        config.logger.error(f"Error in sql select: {err}")
        return
