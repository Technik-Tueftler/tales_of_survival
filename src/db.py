"""
This File contains the database setup, initialization functions and
general database related functions.
"""

from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from .db_classes import INSPIRATIONALWORD, GENRE, EVENT, TALE, STORY, GAME, USER
from .configuration import Configuration


# async def test_db6(config: Configuration):
#     """
#     Test
#     """
#     print(20 * "#" + " Start Test 6 " + 20 * "#")
#     async with config.write_lock:
#         async with config.session() as session:
#             async with session.begin():


async def test_db5(config: Configuration):
    """
    Test
    """
    print(20 * "#" + " Start Test 5 " + 20 * "#")
    async with config.write_lock:
        async with config.session() as session:
            async with session.begin():
                # user = USER()
                genre = GENRE(name="Romance")
                tale = TALE(language="deutsch", genre=genre)
                game = GAME(
                    game_name="PZ",
                    start_date=datetime.now(timezone.utc),
                    message_id=12345678,
                    tale=tale,
                )
                session.add(game)


async def test_db4(config: Configuration):
    """
    Test
    """
    print(20 * "#" + " Start Test 4 " + 20 * "#")
    async with config.session() as session:
        async with session.begin():
            tale = (
                await session.execute(
                    select(TALE)
                    .where(TALE.id == 2)
                    .options(selectinload(TALE.storys))
                )
            ).scalar_one_or_none()
    for story in tale.storys:
        print(story.id, story.story_type.icon)


async def test_db3(config: Configuration):
    """
    Test
    """
    print(20 * "#" + " Start Test 3 " + 20 * "#")
    async with config.write_lock:
        async with config.session() as session:
            async with session.begin():
                genre1 = GENRE(name="Action")
                tale = TALE(language="deutsch", genre=genre1)
                story1 = STORY(request="Anfrage", response="Antwort", tale=tale)
                story2 = STORY(request="Anfrage 2", response="Antwort 2", tale=tale)
                session.add_all([story1, story2])


async def test_db2(config: Configuration):
    """
    Test
    """
    print(20 * "#" + " Start Test 2 " + 20 * "#")
    async with config.write_lock:
        async with config.session() as session:
            async with session.begin():
                genre1 = GENRE(name="Action")
                event1 = EVENT(text="lala blub blub", chance=0.6, genre=genre1)
                event2 = EVENT(text="lala blub blub 2", chance=0.6, genre=genre1)
                session.add_all([event1, event2])
    async with config.session() as session:
        # stmt = select(EVENT).join(EVENT.genre).filter(GENRE.name == "Action")
        stmt = (
            select(EVENT)
            .join(EVENT.genre)
            .where(GENRE.name == "Action")
            .options(selectinload(EVENT.genre))
        )
        events = (await session.execute(stmt)).scalars().all()
        for event in events:
            print(event, event.genre.id)


async def test_db(config: Configuration):
    """
    Test
    """
    print(20 * "#" + " Start Test 1 " + 20 * "#")
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
                tale = TALE(language="deutsch", genre=genre1)
                session.add_all([genre1, genre2])
                session.add(tale)


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
