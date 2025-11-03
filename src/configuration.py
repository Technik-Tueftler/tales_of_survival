"""
Load environment variables and validation of project configurations from user
"""

import random
import asyncio
from typing import List
import environ
from dotenv import load_dotenv
import loguru
from discord.ext.commands import Bot as DcBot
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from .tetue_generic.generic_requests import GenReqConfiguration
from .tetue_generic.watcher import WatcherConfiguration
from .db_classes import (
    DbConfiguration,
    GAME,
    StoryType,
    TALE,
    EVENT,
    CHARACTER,
    GameStatus,
    StartCondition
)


load_dotenv("default.env")
load_dotenv("files/.env", override=True)


class UserContext:
    """
    Class to specify the user context and input data
    for processing.
    """
    def __init__(self):
        self.user_dc_id: str = "0"
        self.available_chars: List[CHARACTER] = []
        self.selected_char: int = 0

    async def input_valid_char(self) -> bool:
        """
        Checks if character are available for selection.

        Returns:
            bool: Character available
        """
        if len(self.available_chars) <= 0:
            return False
        return True


class GameContext:
    """
    Class to specify the game context and input data
    for processing.
    """
    def __init__(self):
        self.available_games: List[GAME] = []
        self.selected_game_id: int = 0
        self.selected_game: GAME = None
        self.new_game_status: GameStatus = None

    async def input_valid_game(self) -> bool:
        """
        Checks if games are available for selection.

        Returns:
            bool: Games available
        """
        if len(self.available_games) <= 0:
            return False
        return True

    async def request_game_start(self) -> bool:
        """
        Checks if a game start is requested, based on the selected game status.

        Returns:
            bool: Game start is requested.
        """
        return (
            self.selected_game.status is GameStatus.CREATED
            and self.new_game_status is GameStatus.RUNNING
        )


class StoryContext:
    """
    Class to specify the story context and input data
    for processing.
    """
    def __init__(self):
        self.story_type: StoryType = None
        self.fiction_prompt: str = ""
        self.tale: TALE = None
        self.event: EVENT = None
        self.character: list[CHARACTER] = []
        self.start = StoryStartContext()

    def events_available(self) -> bool:
        """
        Checks if events are available.

        Returns:
            bool: Events available
        """
        if len(self.tale.genre.events) <= 0:
            return False
        return True

    async def get_random_event_weighted(self):
        """
        Function selecting a random event based on the weights defined
        in the database for the tale's genre.
        """
        weights = [element.chance for element in self.tale.genre.events]
        self.event = random.choices(  # pylint: disable=no-member
            self.tale.genre.events, weights=weights, k=1
        )[0]


class StoryStartContext:
    """
    Class to specify the story start context and input data
    for processing.
    """
    def __init__(self):
        self.condition: StartCondition = None
        self.city: str = ""
        self.prompt: str = ""

class ProcessInput:
    """
    Combined class to hold all context and input data for processing.
    """
    def __init__(self):
        self.user_context = UserContext()
        self.game_context = GameContext()
        self.story_context = StoryContext()


@environ.config(prefix="DC")
class DcConfiguration:
    """
    Configuration model for the discord
    """

    bot_token: str = environ.var(converter=str)


@environ.config(prefix="TT")
class EnvConfiguration:
    """
    Configuration class for the entire application, grouping all sub-configurations.
    """

    api_key = environ.var("ollama", converter=str)
    base_url = environ.var("localhost:11434/v1", converter=str)
    model = environ.var("llama3.2:3b", converter=str)
    gen_req = environ.group(GenReqConfiguration)
    watcher = environ.group(WatcherConfiguration)
    db = environ.group(DbConfiguration)
    dc = environ.group(DcConfiguration)


class Configuration:
    """
    Genral configuration class for the entire application.
    Combines all sub-configurations and initializes the database engine and session.
    """

    def __init__(self, config: EnvConfiguration):
        self.dc_bot = DcBot
        self.env = config
        self.engine = create_async_engine(config.db.db_url)
        self.session = async_sessionmaker(bind=self.engine, expire_on_commit=False)
        self.write_lock = asyncio.Lock()  # pylint: disable=not-callable
        self.logger: loguru._logger.Logger = None
