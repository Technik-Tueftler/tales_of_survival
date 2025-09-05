"""
Load environment variables and validation of project configurations from user
"""
import environ
from dotenv import load_dotenv
from .tetue_generic.generic_requests import GenReqConfiguration
from .tetue_generic.watcher import WatcherConfiguration

load_dotenv("default.env")
load_dotenv("files/.env", override=True)


@environ.config(prefix="TT")
class Configuration:
    """
    Configuration class for the entire application, grouping all sub-configurations.
    """
    gen_req = environ.group(GenReqConfiguration)
    watcher = environ.group(WatcherConfiguration)
