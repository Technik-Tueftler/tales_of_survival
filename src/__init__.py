"""
This module initializes the main application and provides central functions, 
classes and configurations. It serves as the entry point for the entire application 
and enables
- The loading of global configurations and resources.
- The initialization of submodules and packages.
- The import and provision of frequently used functions and constants.
"""
from .configuration import *
from .db_classes import *
from .db import *
from .test import * # TODO: löschen
from .file_utils import *
from .discord_bot import *
from .tetue_generic import __gen_version__
from .tetue_generic.generic_requests import *
from .tetue_generic.watcher import *

__version__ = "v0.1.0"
__repository__ = "https://github.com/Technik-Tueftler/tales_of_survival"
MODE_DEVELOP = False
