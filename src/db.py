"""
This File contains the database setup, initialization functions and
general database related functions.
"""

from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from .db_classes import (
    INSPIRATIONALWORD,
    GENRE,
    EVENT,
    TALE,
    STORY,
    GAME,
    USER,
    CHARACTER,
)
from .configuration import Configuration


async def test_db(config: Configuration):
    await test_db1(config)
    await test_db2(config)
    await test_db3(config)
    await test_db4(config)
    await test_db5(config)
    await test_db6(config)
    await test_db7(config)
    await test_db8(config)


async def test_db8(config: Configuration):
    """
    Test
    """
    print(20 * "#" + " Start Test 8 " + 20 * "#")
    async with config.write_lock:
        async with config.session() as session:
            async with session.begin():
                test_char = CHARACTER(
                    name="Name",
                    age=34,
                    background="jaja",
                    description="nein nein",
                    pos_trait="sehr gut",
                    neg_trait="schnlecht",
                    summary="Sagt zu viel nein",
                )
                session.add(test_char)


async def test_db7(config: Configuration):
    """
    Test
    """
    print(20 * "#" + " Start Test 7 " + 20 * "#")
    async with config.write_lock:
        async with config.session() as session:
            async with session.begin():
                user2 = USER(name="Fire", dc_id="123456789")
                markus_weber = CHARACTER(
                    name="Markus Weber",
                    age=34,
                    background="Gelernter Schreiner, aufgewachsen in einer Kleinstadt in Kentucky.",
                    description="Markus ist ein praktischer, bodenständiger Mann, dessen Hände vom Arbeiten mit Holz und Werkzeugen gezeichnet sind. Schon vor dem Ausbruch war er jemand, der lieber etwas reparierte, anstatt es neu zu kaufen. Sein handwerkliches Geschick macht ihn in einer Welt des Zerfalls zu einem wertvollen Überlebenden – er kann schnell improvisieren und aus begrenzten Ressourcen funktionale Werkzeuge oder Barrikaden bauen. Doch so nützlich diese Fähigkeiten auch sind, Markus trägt auch eine schwer wiegende Schwäche in sich. Er ist ungeschickt im Umgang mit anderen Menschen, denn seit jeher fällt es ihm schwer, Vertrauen zu schenken und im Team zu arbeiten. In Gefahrensituationen neigt er dazu, eigensinnig Entscheidungen zu treffen, manchmal auf Kosten der Gruppe.",
                    pos_trait="Handy (geschickt mit Werkzeugen, kann Reparaturen schneller und effizienter durchführen)",
                    neg_trait="Cowardly / Ängstlich (gerät in Panik, wenn die Situation brenzlig wird, was seine Handlungen unzuverlässig machen kann)",
                    summary="Markus ist ein Überlebender, der zwischen seinem praktischen Talent und seinen inneren Ängsten steht. Seine größte Stärke – sein Können mit den Händen – könnte die Gruppe retten. Doch wenn der Druck zu groß wird, könnten gerade seine Unsicherheiten alles ins Wanken bringen.",
                )
                markus_weber.user = user2
                markus_weber.game_date = datetime.now(timezone.utc)
                session.add(markus_weber)


async def test_db6(config: Configuration):
    """
    Test
    """
    print(20 * "#" + " Start Test 6 " + 20 * "#")
    async with config.write_lock:
        async with config.session() as session:
            async with session.begin():
                genre = GENRE(name="Horror", language="deutsch")
                tale = TALE(genre=genre)
                game = GAME(
                    game_name="Hit and Run with Ice",
                    start_date=datetime.now(timezone.utc),
                    message_id=23456789,
                    tale=tale,
                )
                user = USER(name="Ice", dc_id="123456789")
                game2 = GAME(
                    game_name="Two Hits and Run with Ice",
                    start_date=datetime.now(timezone.utc),
                    message_id=3456780,
                    tale=tale,
                )
                user2 = USER(name="Jo", dc_id="12345678", games=[game2])
                session.add_all([game, user, user2])


async def test_db5(config: Configuration):
    """
    Test
    """
    print(20 * "#" + " Start Test 5 " + 20 * "#")
    async with config.write_lock:
        async with config.session() as session:
            async with session.begin():
                # user = USER()
                genre = GENRE(name="Romance", language="english")
                tale = TALE(genre=genre)
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
                    select(TALE).where(TALE.id == 2).options(selectinload(TALE.stories))
                )
            ).scalar_one_or_none()
    for story in tale.stories:
        print(story.id, story.story_type.icon)


async def test_db3(config: Configuration):
    """
    Test
    """
    print(20 * "#" + " Start Test 3 " + 20 * "#")
    async with config.write_lock:
        async with config.session() as session:
            async with session.begin():
                genre1 = GENRE(name="Action", language="deutsch")
                tale = TALE(genre=genre1)
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
                genre1 = GENRE(name="Action", language="deutsch")
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


async def test_db1(config: Configuration):
    """
    Test
    """
    print(20 * "#" + " Start Test 1 " + 20 * "#")
    async with config.write_lock:
        async with config.session() as session:
            async with session.begin():
                genre1 = GENRE(name="Action", language="deutsch")
                genre2 = GENRE(name="Adventure", language="deutsch")
                insp_word1 = INSPIRATIONALWORD(text="Courage", chance=0.5)
                insp_word2 = INSPIRATIONALWORD(text="Wisdom", chance=0.5)
                insp_word3 = INSPIRATIONALWORD(text="Strength", chance=0.5)
                insp_word4 = INSPIRATIONALWORD(text="Honor", chance=0.5)
                event1 = EVENT(text="A wild beast appears!", chance=0.7)
                event2 = EVENT(text="You find a hidden treasure!", chance=0.3)
                genre1.inspirational_words.extend([insp_word1, insp_word2, insp_word3])
                genre2.inspirational_words.append(insp_word4)
                genre1.events.append(event1)
                genre2.events.append(event2)
                tale = TALE(genre=genre1)
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


async def create_genre_from_input(config: Configuration, data: dict) -> None:
    try:
        final_genre = []
        for genre in data:
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
        async with config.write_lock:
            async with config.session() as session:
                async with session.begin():
                    session.add_all(final_genre)
    except KeyError as err:
        print(err)
    except IntegrityError as err:
        print(err)


async def create_character_from_input(config: Configuration, data: dict) -> None:
    try:
        async with config.write_lock, config.session() as session, session.begin():
            session.add_all(
                [
                    CHARACTER(
                        name=character["name"],
                        age=character["age"],
                        background=character["background"],
                        description=character["description"],
                        pos_trait=character["pos_trait"],
                        neg_trait=character["neg_trait"],
                        summary=character["summary"],
                    )
                    for character in data
                ]
            )
    except IntegrityError as err:
        print(err)


async def get_characters_from_ids(config: Configuration, ids: list[int]) -> None:
    async with config.session() as session, session.begin():
        return (
            (await session.execute(select(CHARACTER).where(CHARACTER.id.in_(ids))))
            .scalars()
            .all()
        )

async def get_all_genre(config: Configuration) -> list[GENRE]:
    async with config.session() as session, session.begin():
        return (
            (await session.execute(select(GENRE)))
            .scalars()
            .all()
        )
