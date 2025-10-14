"""
Load environment variables and validation of project configurations from user
"""
import asyncio
import environ
from dotenv import load_dotenv
import loguru
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from .tetue_generic.generic_requests import GenReqConfiguration
from .tetue_generic.watcher import WatcherConfiguration
from .db_classes import DbConfiguration
from .language import load_locale


load_dotenv("default.env")
load_dotenv("files/.env", override=True)


@environ.config(prefix="LANG")
class LangConfiguration:
    """
    Configuration model for the language
    """
    locale: str = environ.var("en", converter=str)


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
    lang = environ.group(LangConfiguration)


class Configuration:
    """
    Genral configuration class for the entire application.
    Combines all sub-configurations and initializes the database engine and session.
    """
    def __init__(self, config: EnvConfiguration):
        self.env = config
        self.engine = create_async_engine(config.db.db_url)
        self.session = async_sessionmaker(bind=self.engine, expire_on_commit=False)
        self.write_lock = asyncio.Lock() # pylint: disable=not-callable
        self.logger: loguru._logger.Logger = None
        self.locale = load_locale(self.env.lang.locale)
