"""
This module contains all view for game creation and general game handling.
"""

import discord

from .db_classes import GENRE, StoryType
from .configuration import Configuration


class CharacterSelectView(discord.ui.View):
    """
    View class to select a character for a game.
    """

    def __init__(self, config, game_data: dict):
        super().__init__()
        self.add_item(CharacterSelect(config, game_data))


class CharacterSelect(discord.ui.Select):
    """
    Select class to select a character for a game.
    """

    def __init__(self, config, game_data: dict):
        self.config = config
        self.game_data = game_data
        options = [
            discord.SelectOption(
                label=f"{char.id}: {char.name}",
                value=f"{char.id}",
                description=(
                    f"{char.background[:97]}..."
                    if len(char.background) > 100
                    else char.background
                ),
            )
            for char in game_data["available_character"]
        ]

        super().__init__(
            placeholder="Select a character...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        self.config.logger.debug(f"Selected character id: {self.values[0]}")
        self.game_data["selected_character"] = self.values[0]
        await interaction.response.edit_message(
            content=f"You have chosen the character with ID: {self.values[0]}",
        )
        self.view.stop()


class GameSelectAssoc(discord.ui.Select):
    """
    Select class to select a game to set new character.
    """

    def __init__(self, config, game_data: dict):
        self.config = config
        self.game_data = game_data
        options = [
            discord.SelectOption(
                label=f"{assoc.game.id}: {assoc.game.name}",
                value=f"{assoc.id}",
                description=f"Creation date: {assoc.game.start_date}",
            )
            for assoc in game_data["game_association"]
        ]

        super().__init__(
            placeholder="Select a game...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        self.config.logger.debug(f"Selected game id: {self.values[0]}")
        self.game_data["game_association_id"] = self.values[0]
        await interaction.response.edit_message(
            content=f"You have chosen the game with ID: {self.values[0]}",
        )
        self.view.stop()


class GameSelectViewAssoc(discord.ui.View):
    """
    View class to select a genre for a new game.
    """

    def __init__(self, config, game_data: dict):
        super().__init__()
        self.add_item(GameSelectAssoc(config, game_data))


class GameSelect(discord.ui.Select):
    """
    Select class to select a game to set new character.
    """

    def __init__(self, config, game_data: dict):
        self.config = config
        self.game_data = game_data
        options = [
            discord.SelectOption(
                label=f"{game.id}: {game.name}",
                value=f"{game.id}",
                description=f"Creation date: {game.start_date}",
            )
            for game in game_data["available_games"]
        ]

        super().__init__(
            placeholder="Select a game...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        self.config.logger.debug(f"Selected game id: {self.values[0]}")
        self.game_data["selected_game"] = self.values[0]
        await interaction.response.edit_message(
            content=f"You have chosen the game with ID: {self.values[0]}",
        )
        self.view.stop()


class GameSelectView(discord.ui.View):
    """
    View class to select a genre for a new game.
    """

    def __init__(self, config, game_data: dict):
        super().__init__()
        self.add_item(GameSelect(config, game_data))


class GenreSelect(discord.ui.Select):
    """
    Select class to select a genre for a new game.
    """

    def __init__(self, config, game_data: dict, genres: list[GENRE]):
        self.config = config
        self.game_data = game_data
        options = [
            discord.SelectOption(
                label=f"{genre.id}: {genre.name}",
                value=str(genre.id),
                description=f"Style: {genre.storytelling_style}, atmosphere: {genre.atmosphere}",
            )
            for genre in genres
        ]
        super().__init__(
            placeholder="Select a genre...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        self.game_data["genre_id"] = self.values[0]
        game_info_view = GameInfoModal(self.game_data)
        await interaction.response.send_modal(game_info_view)
        await game_info_view.wait()
        self.view.stop()


class GenreSelectView(discord.ui.View):
    """
    View class to select a genre for a new game.
    """

    def __init__(self, config, game_data: dict, genres: list[GENRE]):
        super().__init__()
        self.add_item(GenreSelect(config, game_data, genres))


class GameInfoModal(discord.ui.Modal, title="Please enter the last game information"):
    """
    Modal class to enter general game information.
    """

    def __init__(self, game_data: dict):
        super().__init__()
        self.game_data = game_data
        self.game_name_input = discord.ui.TextInput(
            label="Game name", required=True, max_length=100
        )
        self.add_item(self.game_name_input)

    async def on_submit(
        self, interaction: discord.Interaction
    ):  # pylint: disable=arguments-differ
        """
        Callback function when the modal is submitted.
        """
        self.game_data["game_name"] = self.game_name_input.value
        await interaction.response.edit_message(
            content="All other game information has been entered.",
        )


class UserSelectView(discord.ui.View):
    """
    View class to select user for a new game.
    """

    def __init__(self, config, game_data: dict):
        super().__init__()
        self.config = config
        self.game_data = game_data

    @discord.ui.select(
        cls=discord.ui.UserSelect,
        placeholder="Select up to 6 user for the game",
        min_values=1,
        max_values=6,
    )
    async def user_select(
        self, interaction: discord.Interaction, select: discord.ui.UserSelect
    ):
        """
        Callback function when a user is selected.
        """
        self.game_data["user"] = select.values
        await interaction.response.edit_message(
            content="You have chosen the player for the new game.",
        )
        self.stop()


class StoryFictionModal(discord.ui.Modal, title="Additional text to expand the story"):
    """
    Modal class to enter additional text for the story.
    """

    def __init__(
        self, game_data: dict, parent_view: discord.ui.View, config: Configuration
    ):
        super().__init__()
        self.game_data = game_data
        self.parent_view = parent_view
        self.config = config
        self.story_text_input = discord.ui.TextInput(
            label="Additional text", required=True, style=discord.TextStyle.paragraph
        )
        self.add_item(self.story_text_input)

    async def on_submit(
        self, interaction: discord.Interaction
    ):  # pylint: disable=arguments-differ
        """
        Callback function when the modal is submitted.
        """
        self.game_data["story_text"] = self.story_text_input.value
        self.config.logger.trace(
            f"Additional text for event story type entered: {self.story_text_input.value}"
        )
        await interaction.response.edit_message(
            content="Input completed",
        )
        self.parent_view.stop()


class KeepTellingButtonView(discord.ui.View):
    def __init__(self, config: Configuration, game_data: dict):
        super().__init__()
        self.game_data = game_data
        self.config = config

    @discord.ui.button(
        label=StoryType.FICTION.text,
        style=discord.ButtonStyle.green,
        emoji=StoryType.FICTION.icon,
    )
    async def button_callback_f(self, button, interaction):
        self.game_data["story_type"] = StoryType.FICTION
        self.config.logger.trace(f"Story type selected: {StoryType.FICTION}")
        event_view = StoryFictionModal(self.game_data, self, self.config)
        await button.response.send_modal(event_view)
        await event_view.wait()

    @discord.ui.button(
        label=StoryType.EVENT.text,
        style=discord.ButtonStyle.green,
        emoji=StoryType.EVENT.icon,
    )
    async def button_callback_e(self, button, interaction):
        self.game_data["story_type"] = StoryType.EVENT
        self.config.logger.trace(f"Story type selected: {StoryType.EVENT}")
        await button.response.edit_message(
            content="Input completed",
        )
        self.stop()
