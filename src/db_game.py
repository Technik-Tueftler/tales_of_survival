"""
This file contains the functions to interact with the database for game related operations.
"""

import sys
from typing import List

from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError

from .configuration import Configuration
from .db_classes import (
    CHARACTER,
    GAME,
    USER,
    UserGameCharacterAssociation,
    STORY,
)

class GameInfo:
    """
    This class is used to store all game related information to show  in the 
    game info command. It contains the game, the tale and the user character 
    list with the user and character information.
    """
    def __init__(self):
        self.game: GAME = None
        self.num_stories: int = 0
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
            statement_user = (
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
                (await session.execute(statement_user))
            ).all()
            game_info.user_char_list = [tuple(row) for row in result_user]

            statement = (
                select(
                    func.count(  # pylint: disable=not-callable
                        STORY.id
                    )
                )
                .where(STORY.tale_id == game_info.game.tale_id)
                .where(STORY.response.isnot(None))
                .where(STORY.discarded.is_(False))
            )
            temp_return = (await session.execute(statement)).scalar_one_or_none()
            config.logger.trace(f"Number of stories told: {temp_return}")
            game_info.num_stories = temp_return if temp_return is not None else 0

    except (AttributeError, SQLAlchemyError, TypeError):
        config.logger.opt(exception=sys.exc_info()).error("Error in sql select.")
        return
