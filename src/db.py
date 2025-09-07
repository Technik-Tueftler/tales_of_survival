"""
This File contains the database setup, initialization functions and 
general database related functions.
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine
from .db_classes import Base, Player, Character
from .configuration import Configuration


async def test_db(config: Configuration):
    try:
        async with config.write_lock:
            async with config.session() as session:
                async with session.begin():
                    character = Character(
                        name="Test Character",
                        age=30,
                        background="Test background",
                        description="Test description",
                        pos_trait="Brave",
                        neg_trait="Impulsive",
                        summary="Test summary"
                    )
                    session.add(character)

                    player = Player(
                        alive=True,
                        character=character
                    )
                    session.add(player)
    except Exception as e:
        print(e)
