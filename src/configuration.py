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

    api_key = environ.var("ollama", converter=str)
    base_url = environ.var("http://192.168.178.6:11434/v1", converter=str)
    model = environ.var("llama3.2:3b", converter=str)
    gen_req = environ.group(GenReqConfiguration)
    watcher = environ.group(WatcherConfiguration)
