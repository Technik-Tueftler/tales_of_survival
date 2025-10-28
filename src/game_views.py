"""
This module contains all view for game creation and general game handling.
"""

import discord

from .db_classes import GENRE, StoryType, GameStatus, StartCondition
from .configuration import Configuration, ProcessInput


class CharacterSelectView(discord.ui.View):
    """
    View class to select a character for a game.
    """

    def __init__(self, config, process_data: ProcessInput):
        super().__init__()
        self.add_item(CharacterSelect(config, process_data))


class CharacterSelect(discord.ui.Select):
    """
    Select class to select a character for a game.
    """

    def __init__(self, config, process_data: ProcessInput):
        self.config = config
        self.process_data = process_data
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
            for char in process_data.user_context.available_chars
        ]

        super().__init__(
            placeholder="Select a character...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        self.config.logger.debug(f"Selected character id: {self.values[0]}")
        self.process_data.user_context.selected_char = int(self.values[0])
        await interaction.response.edit_message(
            content=f"You have chosen the character with ID: {self.values[0]}",
        )
        self.view.stop()


class GameSelect(discord.ui.Select):
    """
    Select class to select a game to set new character.
    """

    def __init__(self, config, process_data: ProcessInput):
        self.config = config
        self.process_data = process_data
        options = [
            discord.SelectOption(
                label=f"{game.id}: {game.name}",
                value=f"{game.id}",
                emoji=game.status.icon,
                description=f"{game.status.name}, created: {game.start_date.strftime("%d.%m.%Y")}",
            )
            for game in self.process_data.game_context.available_games
        ]
        super().__init__(
            placeholder="Select a game...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        self.config.logger.debug(f"Selected game id: {self.values[0]}")
        self.process_data.game_context.selected_game_id = int(self.values[0])
        await interaction.response.edit_message(
            content=f"You have chosen the game with ID: {self.values[0]}",
        )
        self.view.stop()


class GameSelectView(discord.ui.View):
    """
    View class to select a genre for a new game.
    """

    def __init__(self, config, process_data: ProcessInput):
        super().__init__()
        self.add_item(GameSelect(config, process_data))


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
        self,
        parent_view: discord.ui.View,
        process_data: ProcessInput,
        config: Configuration,
    ):
        super().__init__()
        self.process_data = process_data
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
        self.process_data.story_context.fiction_prompt = self.story_text_input.value
        self.config.logger.trace(
            f"Additional text for event story type entered: {self.story_text_input.value}"
        )
        await interaction.response.edit_message(
            content="Input completed",
        )
        self.parent_view.stop()


class KeepTellingButtonView(discord.ui.View):
    """
    This view generates buttons for the user to select the next story part
    to continue the story.
    """
    def __init__(self, config: Configuration, process_data: ProcessInput):
        super().__init__()
        self.process_data = process_data
        self.config = config

        for item in self.children:
            if isinstance(item, discord.ui.Button):
                if item.label == StoryType.EVENT.text:
                    item.disabled = not self.process_data.story_context.events_available()

    @discord.ui.button(
        label=StoryType.FICTION.text,
        style=discord.ButtonStyle.green,
        emoji=StoryType.FICTION.icon,
    )
    async def button_callback_f(
        self, button: discord.ui.button, _: discord.interactions.Interaction
    ):
        """
        Callback function when the fiction button is clicked.
        """
        self.process_data.story_context.story_type = StoryType.FICTION
        self.config.logger.trace(f"Story type selected: {StoryType.FICTION}")
        event_view = StoryFictionModal(self, self.process_data, self.config)
        await button.response.send_modal(event_view)
        await event_view.wait()

    @discord.ui.button(
        label=StoryType.EVENT.text,
        style=discord.ButtonStyle.green,
        emoji=StoryType.EVENT.icon,
    )
    async def button_callback_e(
        self, button: discord.ui.button, _: discord.interactions.Interaction
    ):
        """
        Callback function when the event button is clicked.
        """
        self.process_data.story_context.story_type = StoryType.EVENT
        self.config.logger.trace(f"Story type selected: {StoryType.EVENT}")
        await button.response.edit_message(
            content="Input completed",
        )
        self.stop()


class NewGameStatusSelectView(discord.ui.View):
    """
    StatusSelectView class to create a view for the user to select the
    target status of the selected game
    """

    def __init__(self, config: Configuration, process_data: ProcessInput):
        super().__init__()
        self.add_item(NewGameStatusSelect(config, process_data))


class NewGameStatusSelect(discord.ui.Select):
    """
    StatusSelect class to create a input menu to select the target status for the game.
    Here the input is built dynamically with the possible status of a game based on
    current status.
    """

    def __init__(self, config: Configuration, process_data: ProcessInput):
        self.config = config
        self.process_data = process_data
        if process_data.game_context.selected_game.status == GameStatus.CREATED:
            options = [
                discord.SelectOption(
                    label="RUNNING", value=str(GameStatus.RUNNING.value)
                ),
                discord.SelectOption(
                    label="PAUSED", value=str(GameStatus.PAUSED.value)
                ),
            ]
        elif process_data.game_context.selected_game.status == GameStatus.RUNNING:
            options = [
                discord.SelectOption(
                    label="PAUSED", value=str(GameStatus.PAUSED.value)
                ),
            ]
        elif process_data.game_context.selected_game.status == GameStatus.PAUSED:
            options = [
                discord.SelectOption(
                    label="RUNNING", value=str(GameStatus.RUNNING.value)
                ),
                discord.SelectOption(
                    label="STOPPED", value=str(GameStatus.STOPPED.value)
                ),
            ]
        else:
            options = []
            config.logger.error(
                f"Game with ID {process_data.game_context.selected_game.id} is in status "
                + f"{process_data.game_context.selected_game.status}, "
                + "no status change possible."
            )
        super().__init__(
            placeholder="Select the destination status...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        try:
            old_status_name = self.process_data.game_context.selected_game.status.lable
            game_id = self.process_data.game_context.selected_game.id
            new_status = GameStatus(int(self.values[0]))
            self.process_data.game_context.new_game_status = new_status
            await interaction.response.edit_message(
                content=(
                    f"You have changed the status of game {game_id} from {old_status_name} "
                    f"to {new_status.lable}"
                )
            )
            self.view.stop()
        except (IndexError, ValueError) as err:
            self.config.logger.error(f"Error during callback: {err}")
        except discord.errors.Forbidden as err:
            self.config.logger.error(f"Error during callback with DC permissons: {err}")
        except Exception as err:
            print(err, type(err))


class StartTaleButtonView(discord.ui.View):
    """
    This view generates buttons for the user to select the tale type
    to start the story. It is only used during game switch status from
    CREATED to RUNNING.
    """
    def __init__(self, config: Configuration, process_data: ProcessInput):
        super().__init__()
        self.process_data = process_data
        self.config = config

    @discord.ui.button(
        label=StartCondition.S_ZOMBIE_X.text,
        style=discord.ButtonStyle.green,
        emoji=StartCondition.S_ZOMBIE_X.icon,
    )
    async def button_callback_x(
        self, button: discord.ui.button, _: discord.interactions.Interaction
    ):
        """
        Callback function when button for standard zombie tale with more then 1 player is clicked.
        """
        self.process_data.story_context.start_condition = StartCondition.S_ZOMBIE_X
        self.config.logger.trace(f"Start tale type selected: {StartCondition.S_ZOMBIE_X.text}")
        event_view = StZombieTaleStartModal(self, self.process_data, self.config)
        await button.response.send_modal(event_view)
        await event_view.wait()

    @discord.ui.button(
        label=StartCondition.S_ZOMBIE_1.text,
        style=discord.ButtonStyle.green,
        emoji=StartCondition.S_ZOMBIE_1.icon,
    )
    async def button_callback_1(
        self, button: discord.ui.button, _: discord.interactions.Interaction
    ):
        """
        Callback function when button for standard zombie tale with one player is clicked.
        """
        self.process_data.story_context.start_condition = StartCondition.S_ZOMBIE_1
        self.config.logger.trace(f"Start tale type selected: {StartCondition.S_ZOMBIE_1.text}")
        event_view = StZombieTaleStartModal(self, self.process_data, self.config)
        await button.response.send_modal(event_view)
        await event_view.wait()

    @discord.ui.button(
        label=StartCondition.OWN_X.text,
        style=discord.ButtonStyle.green,
        emoji=StartCondition.OWN_X.icon,
    )
    async def button_callback_ox(
        self, button: discord.ui.button, _: discord.interactions.Interaction
    ):
        """
        Callback function when button for own tale with more then 1 player is clicked.
        """
        self.process_data.story_context.start_condition = StartCondition.OWN_X
        self.config.logger.trace(f"Start tale type selected: {StartCondition.OWN_X.text}")
        event_view = OwnTaleStartModal(self, self.process_data, self.config)
        await button.response.send_modal(event_view)
        await event_view.wait()

    @discord.ui.button(
        label=StartCondition.OWN_1.text,
        style=discord.ButtonStyle.green,
        emoji=StartCondition.OWN_1.icon,
    )
    async def button_callback_o1(
        self, button: discord.ui.button, _: discord.interactions.Interaction
    ):
        """
        Callback function when button for own tale with one player is clicked.
        """
        self.process_data.story_context.start_condition = StartCondition.OWN_1
        self.config.logger.trace(f"Start tale type selected: {StartCondition.OWN_1.text}")
        event_view = OwnTaleStartModal(self, self.process_data, self.config)
        await button.response.send_modal(event_view)
        await event_view.wait()


class OwnTaleStartModal(discord.ui.Modal, title="Additional input for your tale:"):
    """
    Modal class to enter additional text for the story.
    """

    def __init__(
        self,
        parent_view: discord.ui.View,
        process_data: ProcessInput,
        config: Configuration,
    ):
        super().__init__()
        self.process_data = process_data
        self.parent_view = parent_view
        self.config = config
        self.location_input = discord.ui.TextInput(
            label="Start location",
            placeholder="Enter the starting location for the tale.",
            required=True,
            min_length=1,
            max_length=100,
            style=discord.TextStyle.short,
        )
        self.prompt_input = discord.ui.TextInput(
            label="KI Prompt",
            placeholder="Your prompt for the AI.",
            required=True,
            min_length=1,
            max_length=512,
            style=discord.TextStyle.paragraph,
        )
        self.add_item(self.location_input)
        self.add_item(self.prompt_input)

    async def on_submit(
        self, interaction: discord.Interaction
    ):
        if not self.location_input.value.strip():
            await interaction.response.send_message(
                "The start location field must not be left blank.", ephemeral=True
            )
            return
        if not self.prompt_input.value.strip():
            await interaction.response.send_message(
                "The AI prompt field must not be left blank.", ephemeral=True
            )
            return

        self.process_data.story_context.start_city = self.location_input.value
        self.process_data.story_context.start_prompt = self.prompt_input.value
        self.config.logger.debug(
            f"Start location: {self.location_input.value}, KI Prompt: {self.prompt_input.value}"
        )
        await interaction.response.edit_message(
            content="Input completed",
        )
        self.parent_view.stop()


class StZombieTaleStartModal(discord.ui.Modal, title="Additional input for your zombie tale:"):
    """
    Modal class to enter additional text for the story.
    """

    def __init__(
        self,
        parent_view: discord.ui.View,
        process_data: ProcessInput,
        config: Configuration,
    ):
        super().__init__()
        self.process_data = process_data
        self.parent_view = parent_view
        self.config = config
        self.location_input = discord.ui.TextInput(
            label="Start location",
            placeholder="Enter the starting location for the tale.",
            required=True,
            min_length=1,
            max_length=100,
            style=discord.TextStyle.short,
        )
        self.prompt_input = discord.ui.TextInput(
            label="KI Prompt",
            placeholder="Your prompt for the AI.",
            required=False,
            min_length=1,
            max_length=512,
            style=discord.TextStyle.paragraph,
        )
        self.add_item(self.location_input)
        self.add_item(self.prompt_input)

    async def on_submit(
        self, interaction: discord.Interaction
    ):
        if not self.location_input.value.strip():
            await interaction.response.send_message(
                "The start location field must not be left blank.", ephemeral=True
            )
            return

        print(self.prompt_input.value)
        self.process_data.story_context.start_city = self.location_input.value
        self.process_data.story_context.start_prompt = self.prompt_input.value
        self.config.logger.debug(
            f"Start location: {self.location_input.value}, KI Prompt: {self.prompt_input.value}"
        )
        await interaction.response.edit_message(
            content="Input completed",
        )
        self.parent_view.stop()
