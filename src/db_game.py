"""
This file contains the functions to interact with the database for game related operations.
"""

import sys
from dataclasses import dataclass
from typing import List

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
    TALE,
    USER,
    UserGameCharacterAssociation,
    GameStatus,
    STORY,
    StoryType,
    MESSAGE,
)

class GameInfo:
    """
    This class is used to store all game related information to show  in the 
    game info command. It contains the game, the tale and the user character 
    list with the user and character information.
    """
    def __init__(self):
        self.game: GAME = None
        self.tale: TALE = None
        self.user_char_list: List[tuple[USER, CHARACTER]] = []


async def get_all_game_related_infos(
    config: Configuration, game_info: GameInfo
) -> None:
    """
    Function get all games loaded with user participations from the database from a user.

    Args:
        config (Configuration): App configuration
        game_info (GameInfo): Game info data structure
    """
    try:
        async with config.session() as session, session.begin():
            statement = (
                select(USER, CHARACTER)
                .join(
                    UserGameCharacterAssociation,
                    USER.id == UserGameCharacterAssociation.user_id,
                )
                .join(
                    CHARACTER, CHARACTER.id == UserGameCharacterAssociation.character_id
                )
                .where(
                    UserGameCharacterAssociation.game_id
                    == game_info.game.id
                )
                .where(UserGameCharacterAssociation.end_date.is_(None))
            )
            result_user = (
                (await session.execute(statement))
            ).all()
            game_info.user_char_list = [tuple(row) for row in result_user]

    except (AttributeError, SQLAlchemyError, TypeError):
        config.logger.opt(exception=sys.exc_info()).error("Error in sql select.")
        return
