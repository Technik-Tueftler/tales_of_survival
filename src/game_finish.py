"""
Module to handle game finish actions and commands, including processing 
and generating the final story.
"""

from discord import Interaction
from .discord_utils import (
    interface_select_game,
)
from .configuration import Configuration, ProcessInput
from .db_classes import GameStatus
from .db import (
    get_games_w_status,
)
from .game_views import (
    GameFinishView,
    StoryFinishView,
)


async def finish_game(interaction: Interaction, config: Configuration) -> None:
    """
    This function finishes a game and generates a PDF with the story so far.
    The game status will be set to finished. It is not possible to keep
    telling a story after finishing the game.
    Args:
        interaction (Interaction): Discord interaction object
        config (Configuration): App configuration
    """
    process_data = ProcessInput()
    process_data.game_context.available_games = await get_games_w_status(
        config,
        [
            GameStatus.STOPPED,
        ],
    )
    select_success = await interface_select_game(interaction, config, process_data)
    if not select_success:
        return
    game_finish_view = GameFinishView(config, process_data)
    await interaction.followup.send(
        "Are you sure you want to finish the game with ID: "
        + f"{process_data.game_context.selected_game_id}? "
        + "It will not be possible to restart it!",
        view=game_finish_view,
        ephemeral=True,
    )
    await game_finish_view.wait()

    if not process_data.game_context.finish.finish_confirmed:
        return
    print("Finish game")
    try:
        story_output_view = StoryFinishView(config, process_data)
        await interaction.followup.send(view=story_output_view, ephemeral=True)
        await story_output_view.wait()
        print("Finished game")
    except Exception as err:
        print(err)