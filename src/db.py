"""
This File contains the database setup, initialization functions and
general database related functions.
"""

import sys
from dataclasses import dataclass

import discord
from sqlalchemy import select, func, exists, update
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
    STORY,
    StoryType,
    MESSAGE,
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
    text_genre: str = ""
    text_character: str = ""


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


async def check_exist_unique_character(config: Configuration, character: dict) -> bool:
    """
    Function checks whether the character passed is unique.

    Args:
        config (Configuration): App configuration
        genre (dict): New character from yml load

    Returns:
        bool: Transferred character already exists.
    """
    try:
        async with config.session() as session, session.begin():
            statement = select(exists().where(CHARACTER.name == character["name"]))
            return (await session.execute(statement)).scalar()
    except (AttributeError, SQLAlchemyError, TypeError):
        config.logger.opt(exception=sys.exc_info()).error("Error in sql select.")
        return False


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


async def create_character_from_input(config: Configuration, result: ImportResult):
    """
    Function to create character from imported file.

    Args:
        config (Configuration): App configuration
        result (ImportResult): Result class from importing a file
    """
    try:
        missed_character = []
        final_character = []
        for character in result.data:
            if await check_exist_unique_character(config, character):
                config.logger.debug(
                    f"The following character already exist: {character["name"]}"
                )
                missed_character.append(character["name"])
                continue
            temp_character = CHARACTER(
                name=character["name"],
                age=character["age"],
                background=character["background"],
                description=character["description"],
                pos_trait=character["pos_trait"],
                neg_trait=character["neg_trait"],
                summary=character["summary"],
            )
            final_character.append(temp_character)
        async with config.write_lock, config.session() as session, session.begin():
            session.add_all(final_character)
        result.import_number = len(final_character)
        result.success = True
        if missed_character:
            result.text_character = (
                "The following characters already exist with the settings "
                + f"provided: {", ".join(missed_character)}. "
            )
    except (KeyError, IntegrityError):
        config.logger.opt(exception=sys.exc_info()).error(
            "Error while import character file."
        )


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
    except (AttributeError, SQLAlchemyError, TypeError):
        config.logger.opt(exception=sys.exc_info()).error("Error in sql update.")
        return


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
                return []
            config.logger.trace("Available characters retrieved from database")
            return result

    except (AttributeError, SQLAlchemyError, TypeError):
        config.logger.opt(exception=sys.exc_info()).error("Error in sql select.")
        return []
    

async def get_all_owned_characters(config: Configuration, user: USER) -> list[CHARACTER]:
    """
    Function to get all characters from the database which are assigned to a user and
    assigned to a not finished game.

    Args:
        config (Configuration): App configuration
        user (USER): User object
    """
    try:
        async with config.session() as session, session.begin():
            statement = (
                select(CHARACTER)
                .join(CHARACTER.game_assignments)
                .join(UserGameCharacterAssociation.game)
                .join(UserGameCharacterAssociation.user)
                .where(
                    USER.id == user.id,
                    GAME.end_date.is_(None),
                    CHARACTER.alive.is_(True),
                    CHARACTER.end_date.is_(None),
                )
                .distinct()
            )
            result = (await session.execute(statement)).scalars().all()

            if result is None or len(result) == 0:
                config.logger.debug("No available characters found in the database")
                return []
            config.logger.trace("Available characters retrieved from database")
            return result

    except (AttributeError, SQLAlchemyError, TypeError):
        config.logger.opt(exception=sys.exc_info()).error("Error in sql select.")
        return []


async def get_all_open_user_games(
    config: Configuration, process_data: ProcessInput
) -> None:
    """
    Function get all games loaded with user participations from the database from a user.

    Args:
        config (Configuration): App configuration
        process_data (ProcessInput): Process input data structure
    """
    try:
        async with config.session() as session, session.begin():
            statement = (
                select(GAME)
                .join(GAME.user_participations)
                .join(UserGameCharacterAssociation.user)
                .where(USER.dc_id == process_data.user_context.user_dc_id)
                .where(UserGameCharacterAssociation.character_id.is_(None))
                .where(UserGameCharacterAssociation.end_date.is_(None))
            )
            process_data.game_context.available_games = (
                (await session.execute(statement)).scalars().all()
            )

    except (AttributeError, SQLAlchemyError, TypeError):
        config.logger.opt(exception=sys.exc_info()).error("Error in sql select.")
        return


async def get_all_running_games(
    config: Configuration, process_data: ProcessInput
) -> None:
    """
    Function to get all available games from the database which are not finished.

    Args:
        config (Configuration): App configuration
        process_data (ProcessInput): Game data object
    """
    try:
        async with config.session() as session, session.begin():
            statement = (
                select(GAME)
                .where(GAME.end_date.is_(None))
                .where(GAME.status == GameStatus.RUNNING)
            )
            result = (await session.execute(statement)).scalars().all()

            if result is None or len(result) == 0:
                config.logger.debug("No available games found in the database")
                return
            process_data.game_context.available_games = result

    except (AttributeError, SQLAlchemyError, TypeError):
        config.logger.opt(exception=sys.exc_info()).error("Error in sql select.")
        return


async def get_tale_from_game_id(config: Configuration, game_id: int) -> TALE | None:
    """
    Function to get the tale based on handed over game id.

    Args:
        config (Configuration): App configuration
        game_id (int): Game id

    Returns:
        TALE | None: One Tale or None
    """
    try:
        async with config.session() as session, session.begin():
            statement = (
                select(TALE)
                .join(TALE.game)
                .options(
                    joinedload(TALE.genre).options(
                        selectinload(GENRE.events),
                        selectinload(GENRE.inspirational_words),
                    ),
                    joinedload(TALE.game).options(
                        selectinload(GAME.user_participations)
                    ),
                )
                .where(GAME.id == game_id)
            )
            return (await session.execute(statement)).scalar_one_or_none()

    except (AttributeError, SQLAlchemyError, TypeError):
        config.logger.opt(exception=sys.exc_info()).error("Error in sql select.")
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


async def get_user_from_dc_id(config: Configuration, dc_id: str) -> USER | None:
    """
    Get the user object based on handed over discord id.

    Args:
        config (Configuration): App configuration
        dc_id (str): Discord ID of user

    Returns:
        USER | None: One User or None
    """
    try:
        async with config.session() as session, session.begin():
            statement = select(USER).where(USER.dc_id == dc_id)
            return (await session.execute(statement)).scalar_one_or_none()

    except (AttributeError, SQLAlchemyError, TypeError):
        config.logger.opt(exception=sys.exc_info()).error("Error in sql select.")
        return


async def get_mapped_ugc_association(
    config: Configuration, game_id: int, user_id: int
) -> UserGameCharacterAssociation | None:
    """
    Function get the association object based on handed over game and user id.

    Args:
        config (Configuration): App configuration
        game_id (int): Game id
        user_id (int): User id

    Returns:
        UserGameCharacterAssociation | None: Linked association object
    """
    try:
        async with config.session() as session, session.begin():
            statement = (
                select(UserGameCharacterAssociation)
                .where(UserGameCharacterAssociation.game_id == game_id)
                .where(UserGameCharacterAssociation.user_id == user_id)
            )
            return (await session.execute(statement)).scalar_one_or_none()

    except (AttributeError, SQLAlchemyError, TypeError):
        config.logger.opt(exception=sys.exc_info()).error("Error in sql select.")
        return


async def count_regist_char_from_game(config: Configuration, game_id: int) -> int:
    """
    Function get the number of registered character in a handed over game based on id.

    Args:
        config (Configuration): App configuration
        game_id (int): Game id

    Returns:
        int: Count of registered characters
    """
    try:
        async with config.session() as session, session.begin():
            statement = (
                select(
                    func.count(  # pylint: disable=not-callable
                        UserGameCharacterAssociation.id
                    )
                )
                .where(UserGameCharacterAssociation.game_id == game_id)
                .where(UserGameCharacterAssociation.character_id.isnot(None))
                .where(UserGameCharacterAssociation.end_date.is_(None))
            )
            temp_return = (await session.execute(statement)).scalar_one_or_none()
            config.logger.trace(f"Counted registered character: {temp_return}")
            return temp_return

    except (AttributeError, SQLAlchemyError, TypeError):
        config.logger.opt(exception=sys.exc_info()).error("Error in sql select.")
        return 0


async def get_active_user_from_game(
    config: Configuration, game_id: int
) -> list[USER] | None:
    """
    Function get all active user based on game ID and if a character is selected in game
    association.

    Args:
        config (Configuration): App configuration
        game_id (int): Game ID

    Returns:
        list[USER] | None: All active user in game or None
    """
    try:
        async with config.session() as session, session.begin():
            statement = (
                select(USER)
                .join(
                    UserGameCharacterAssociation,
                    USER.id == UserGameCharacterAssociation.user_id,
                )
                .where(UserGameCharacterAssociation.game_id == game_id)
                .where(UserGameCharacterAssociation.character_id.isnot(None))
                .distinct(USER.id)
            )
            return (await session.execute(statement)).scalars().all()
    except (AttributeError, SQLAlchemyError, TypeError):
        config.logger.opt(exception=sys.exc_info()).error("Error in sql select.")
        return None


async def get_character_from_game_id(
    config: Configuration, game_id: int
) -> list[CHARACTER] | None:
    """
    Function get all registered characters from a game based on handed over game id.

    Args:
        config (Configuration): App configuration
        game_id (int): Game id

    Returns:
        list[CHARACTER] | None: List of characters or None
    """
    try:
        async with config.session() as session, session.begin():
            statement = (
                select(CHARACTER)
                .join(
                    UserGameCharacterAssociation,
                    UserGameCharacterAssociation.character_id == CHARACTER.id,
                )
                .where(UserGameCharacterAssociation.game_id == game_id)
            )
            return (await session.execute(statement)).scalars().all()
    except (AttributeError, SQLAlchemyError, TypeError):
        config.logger.opt(exception=sys.exc_info()).error("Error in sql select.")


async def get_stories_messages_for_ai(
    config: Configuration, tale_id: int
) -> list[dict]:
    """
    This function retrieves all stories for a given tale id and formats them
    into a list of messages suitable for AI processing.

    Args:
        config (Configuration): App configuration
        tale_id (int): Tale ID to retrieve stories

    Returns:
        list[dict]: List of messages formatted for AI
    """
    try:
        async with config.session() as session, session.begin():
            statement = (
                select(STORY)
                .where(STORY.tale_id == tale_id)
                .where(STORY.discarded.is_(False))
                .order_by(STORY.id)
            )
            stories = (await session.execute(statement)).scalars().all()
        if stories is None or len(stories) == 0:
            config.logger.debug(f"No stories found for tale id: {tale_id}")
            return []
        messages = []
        for story in stories:
            if story.request is not None and story.request != "":
                messages.append({"role": "user", "content": story.request})
            elif story.response is not None and story.response != "":
                messages.append({"role": "assistant", "content": story.response})
            else:
                config.logger.warning(
                    f"Story with id {story.id} has no request or response."
                )
        return messages
    except (AttributeError, SQLAlchemyError, TypeError):
        config.logger.opt(exception=sys.exc_info()).error("Error in sql select.")
        return []


async def channel_id_exist(config: Configuration, channel_id: str) -> bool:
    """
    This function checks if a channel ID exists in a game.

    Args:
        config (Configuration): App configuration
        channel_id (str): Channel ID

    Returns:
        bool: Any game started with same channel ID
    """
    try:
        async with config.session() as session, session.begin():
            statement = select(exists().where(GAME.channel_id == channel_id))
            return (await session.execute(statement)).scalar()

    except (AttributeError, SQLAlchemyError, TypeError):
        config.logger.opt(exception=sys.exc_info()).error("Error in sql select.")
        return True


async def check_only_init_stories(config: Configuration, tale_id: int) -> bool:
    """
    This function checks whether there are stories that have a story type other than INIT.

    Args:
        config (Configuration): App configuration
        tale_id (int): Tale id to get all stories

    Returns:
        bool: Identify whether there are only stories that have the type INIT.
    """
    async with config.session() as session, session.begin():
        statement = (
            select(STORY)
            .where(STORY.tale_id == tale_id)
            .where(STORY.story_type != StoryType.INIT)
            .where(STORY.discarded.is_(False))
        )
        stories = (await session.execute(statement)).scalars().all()
    if len(stories) <= 0:
        return True
    return False


async def delete_init_stories(
    config: Configuration, tale_id: int, game_id: int
) -> list[int]:
    """
    This function deletes all INIT stories from a tale and returns the Discord
    message IDs associated with those stories.

    Args:
        config (Configuration): App configuration
        tale_id (int): Tale ID to delete stories from
        game_id (int): Game ID

    Returns:
        list[int]: List of Discord message IDs that were associated with the deleted stories
    """
    async with config.session() as session, session.begin():
        statement_stories = (
            select(STORY)
            .where(STORY.tale_id == tale_id)
            .where(STORY.discarded.is_(False))
        )
        stories = (await session.execute(statement_stories)).scalars().all()
        story_ids = [story.id for story in stories]
        config.logger.debug(f"Select stories with IDs: {story_ids} for discarding.")
        statement_messages = select(MESSAGE).where(MESSAGE.story_id.in_(story_ids))
        messages = (await session.execute(statement_messages)).scalars().all()
        config.logger.debug(
            f"Select messages with IDs: {[message.id for message in messages]} for deleting."
        )
        dc_message_ids = [
            message.message_id for message in messages if message.message_id is not None
        ]
        config.logger.debug(f"DC messages IDs to delete: {dc_message_ids}")
        for message in messages:
            await session.delete(message)
        config.logger.debug(f"Deleted {len(messages)} messages.")

        statement_messages = (
            update(STORY).where(STORY.id.in_(story_ids)).values(discarded=True)
        )
        await session.execute(statement_messages)
        config.logger.debug(f"Discard {len(messages)} stories.")
        statement_game = select(GAME).where(GAME.id == game_id)
        game = (await session.execute(statement_game)).scalar_one_or_none()
        game.status = GameStatus.CREATED
        return dc_message_ids


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


async def get_all_running_user_games(
    config: Configuration, process_data: ProcessInput
) -> None:
    """
    Function get all running games loaded with user participations from the database from a user.

    Args:
        config (Configuration): App configuration
        process_data (ProcessInput): Process input data structure
    """
    try:
        async with config.session() as session, session.begin():
            statement = (
                select(GAME)
                .join(GAME.user_participations)
                .join(UserGameCharacterAssociation.user)
                .where(GAME.end_date.is_(None))
                .where(GAME.status == GameStatus.RUNNING)
                .where(USER.dc_id == process_data.user_context.user_dc_id)
                .where(UserGameCharacterAssociation.character_id.isnot(None))
            )
            process_data.game_context.available_games = (
                (await session.execute(statement)).scalars().all()
            )

    except (AttributeError, SQLAlchemyError, TypeError):
        config.logger.opt(exception=sys.exc_info()).error("Error in sql select.")
        return
