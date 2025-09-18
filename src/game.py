from discord import Interaction
from .configuration import Configuration

async def create_game(interaction: Interaction, config: Configuration):
    print("Create Game")

async def keep_telling(interaction: Interaction, config: Configuration):
    print("Keep telling")
