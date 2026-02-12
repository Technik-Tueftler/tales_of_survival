"""This module handles all genre related operations for the Discord bot."""

import sys
import asyncio
import discord
from discord import Interaction
from .db import (
    update_db_objs,
)
from .db_genre import (
    get_loaded_genre_from_id,
    get_active_genre,
    deactivate_genre_with_id,
    get_inactive_genre,
    activate_genre_with_id,
)
from .db_classes import EVENT, INSPIRATIONALWORD
from .file_utils import limit_text
from .configuration import Configuration, GenreContext
from .constants import (
    DC_MODAL_INPUT_EVENT_TEXT_MAX_CHAR,
    DC_MODAL_INPUT_EVENT_TEXT_MIN_CHAR,
    DC_MODAL_INPUT_WORD_TEXT_MAX_CHAR,
    DC_MODAL_INPUT_WORD_TEXT_MIN_CHAR,
)


class GenreSelectView(discord.ui.View):
    """
    View class to select a genre for a new game.
    """

    def __init__(self, config, process_data: GenreContext):
        super().__init__()
        self.add_item(GenreSelect(config, process_data))


class GenreSelect(discord.ui.Select):
    """
    Select class to select a genre for a new game.
    """

    def __init__(self, config: Configuration, process_data: GenreContext):
        self.config = config
        self.process_data = process_data
        options = []
        for genre in process_data.available_genre:
            description = (
                f"Style: {genre.storytelling_style}, "
                + f"atmosphere: {genre.atmosphere}, "
                + f"language: {genre.language}"
            )
            options.append(
                discord.SelectOption(
                    label=f"{genre.id}: {genre.name}",
                    value=str(genre.id),
                    description=limit_text(description),
                )
            )
        super().__init__(
            placeholder="Select a genre...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        selected_option = [
            option for option in self.options if option.value == self.values[0]
        ]
        self.config.logger.debug(f"Selected genre id: {self.values[0]}")
        self.process_data.selected_genre_id = int(self.values[0])
        label = selected_option[0].label
        self.disabled = True
        await interaction.response.edit_message(
            content=f"You have chosen the genre {label}", view=self.view
        )
        self.view.stop()


async def single_genre_selection(
    interaction: Interaction, config: Configuration, genre_context: GenreContext
) -> None:
    """
    This function is a generic implementation to select a single genre from hand over list of
    available genres.

    Args:
        interaction (Interaction): Dicord interaction object
        config (Configuration): App configuration
        genre_context (GenreContext): Genre context object
    """
    try:
        if not await genre_context.input_valid_genre():
            config.logger.debug("Call function with no available genre.")
            await interaction.response.send_message(
                "No genre available for the called command, please contact a Mod.",
                ephemeral=True,
            )
            return

        genre_select_view = GenreSelectView(config, genre_context)
        await interaction.response.send_message(
            "Please select a genre for your command:",
            view=genre_select_view,
            ephemeral=True,
        )
        await genre_select_view.wait()

        if genre_context.selected_genre_id == 0:
            config.logger.debug("No selection during genre selection call from user.")
            await interaction.followup.send(
                "No genre was selected, cancelling command.",
                ephemeral=True,
            )
            return
        genre_context.selected_genre = await get_loaded_genre_from_id(
            config, genre_context.selected_genre_id
        )
    except discord.HTTPException:
        config.logger.opt(exception=sys.exc_info()).error("Failed to send message.")
    except (TypeError, ValueError):
        config.logger.opt(exception=sys.exc_info()).error("General error occurred.")
    except asyncio.TimeoutError:
        config.logger.opt(exception=sys.exc_info()).error("Timeout error occurred.")


async def deactivate_genre(interaction: Interaction, config: Configuration) -> None:
    """
    This function allows the user to deactivate a genre.

    Args:
        interaction (Interaction): Discord interaction object
        config (Configuration): App configuration
    """
    try:
        process_data = GenreContext()
        process_data.available_genre = await get_active_genre(config)
        await single_genre_selection(interaction, config, process_data)

        if process_data.selected_genre is None:
            config.logger.trace(
                f"No genre available for the ID: {process_data.selected_genre_id}"
            )
            return

        await deactivate_genre_with_id(config, process_data.selected_genre_id)
        await interaction.followup.send(
            "Genre is deactivated successfully.",
            ephemeral=True,
        )
    except discord.Forbidden:
        config.logger.opt(exception=sys.exc_info()).error(
            "Cannot send message, permission denied."
        )
    except discord.HTTPException:
        config.logger.opt(exception=sys.exc_info()).error("Failed to send message.")
    except (TypeError, ValueError):
        config.logger.opt(exception=sys.exc_info()).error("General error occurred.")
    except asyncio.TimeoutError:
        config.logger.opt(exception=sys.exc_info()).error("Timeout error occurred.")


async def activate_genre(interaction: Interaction, config: Configuration) -> None:
    """
    This function allows the user to activate a genre.

    Args:
        interaction (Interaction): Discord interaction object
        config (Configuration): App configuration
    """
    try:
        process_data = GenreContext()
        process_data.available_genre = await get_inactive_genre(config)

        await single_genre_selection(interaction, config, process_data)

        if process_data.selected_genre is None:
            config.logger.trace(
                f"No genre available for the ID: {process_data.selected_genre_id}"
            )
            return
        await activate_genre_with_id(config, process_data.selected_genre_id)
        await interaction.followup.send(
            "Genre is activated successfully.",
            ephemeral=True,
        )
    except discord.HTTPException:
        config.logger.opt(exception=sys.exc_info()).error("Failed to send message.")
    except (TypeError, ValueError):
        config.logger.opt(exception=sys.exc_info()).error("General error occurred.")
    except asyncio.TimeoutError:
        config.logger.opt(exception=sys.exc_info()).error("Timeout error occurred.")


class AddEventToGenreModal(discord.ui.Modal, title="Define a new event for the genre"):
    """
    Text modal to add a new event to a specific genre.

    Args:
        parent_view (discord.ui.View): Parent view of the modal
        config (Configuration): App configuration
        genre_context (GenreContext): Genre context object
    """

    def __init__(
        self,
        parent_view: discord.ui.View,
        config: Configuration,
        genre_context: GenreContext,
    ):
        super().__init__()
        self.parent_view = parent_view
        self.config = config
        self.genre_context = genre_context
        self.text = discord.ui.TextInput(
            label="Event text",
            placeholder="Describe the event that can occur in this genre.",
            required=True,
            min_length=DC_MODAL_INPUT_EVENT_TEXT_MIN_CHAR,
            max_length=DC_MODAL_INPUT_EVENT_TEXT_MAX_CHAR,
            style=discord.TextStyle.paragraph,
        )
        self.chance = discord.ui.TextInput(
            label="Event chance in %",
            placeholder="Enter a chance for the event (e.g. 20 for 20%)",
            required=True,
            min_length=1,
            max_length=2,
            style=discord.TextStyle.short,
        )
        self.add_item(self.text)
        self.add_item(self.chance)

    async def on_submit(  # pylint: disable=arguments-differ
        self, interaction: discord.Interaction
    ):
        if not self.text.value.strip():
            await interaction.response.send_message(
                "The event text field must not be left blank.", ephemeral=True
            )
            self.config.logger.debug(
                f"Event text input is invalid: '{self.text.value}'"
            )
            return
        if not (self.chance.value.isdigit() and 0 < int(self.chance.value) <= 100):
            await interaction.response.send_message(
                "Value must be a positive integer between 1 and 99", ephemeral=True
            )
            self.config.logger.debug(
                f"Event chance input is invalid: '{self.chance.value}'"
            )
            return
        self.genre_context.selected_genre.events.append(
            EVENT(text=self.text.value, chance=int(self.chance.value))
        )
        self.config.logger.debug(
            f"New event is generated for genre id: {self.genre_context.selected_genre.id}"
        )
        await update_db_objs(self.config, [self.genre_context.selected_genre])
        await interaction.response.send_message(
            content=f"Event added successfully to genre: {self.genre_context.selected_genre.name}",
        )
        self.parent_view.stop()


class AddWordsToGenreModal(discord.ui.Modal, title="Define new words for the genre"):
    """
    Text modal to add new inspirational words to a specific genre.

    Args:
        parent_view (discord.ui.View): Parent view of the modal
        config (Configuration): App configuration
        genre_context (GenreContext): Genre context object
    """

    def __init__(
        self,
        parent_view: discord.ui.View,
        config: Configuration,
        genre_context: GenreContext,
    ):
        super().__init__()
        self.parent_view = parent_view
        self.config = config
        self.genre_context = genre_context
        self.word_1 = discord.ui.TextInput(
            label="Word",
            placeholder="Enter an inspirational word for the genre.",
            required=False,
            min_length=DC_MODAL_INPUT_WORD_TEXT_MIN_CHAR,
            max_length=DC_MODAL_INPUT_WORD_TEXT_MAX_CHAR,
            style=discord.TextStyle.short,
        )
        self.chance_1 = discord.ui.TextInput(
            label="Word chance in %",
            placeholder="Enter a chance for the word (e.g. 20 for 20%)",
            required=False,
            min_length=1,
            max_length=2,
            style=discord.TextStyle.short,
        )
        self.word_2 = discord.ui.TextInput(
            label="Word",
            placeholder="Enter an inspirational word for the genre.",
            required=False,
            min_length=DC_MODAL_INPUT_WORD_TEXT_MIN_CHAR,
            max_length=DC_MODAL_INPUT_WORD_TEXT_MAX_CHAR,
            style=discord.TextStyle.short,
        )
        self.chance_2 = discord.ui.TextInput(
            label="Word chance in %",
            placeholder="Enter a chance for the word (e.g. 20 for 20%)",
            required=False,
            min_length=1,
            max_length=2,
            style=discord.TextStyle.short,
        )
        self.add_item(self.word_1)
        self.add_item(self.chance_1)
        self.add_item(self.word_2)
        self.add_item(self.chance_2)

    async def on_submit(  # pylint: disable=arguments-differ
        self, interaction: discord.Interaction
    ):
        faulty_words = []
        valid_words = {}
        valid_text = ""
        faulty_text = ""
        pairs = [
            (self.word_1.value, self.chance_1.value),
            (self.word_2.value, self.chance_2.value),
        ]
        for index, (word, chance) in enumerate(pairs, start=1):
            if word.strip():
                if chance.isdigit() and 0 < int(chance) <= 100:
                    valid_words[word.strip()] = int(chance)
                else:
                    self.config.logger.debug(
                        f"Word {index} has invalid chance input: '{chance}'"
                    )
                    faulty_words.append(str(index))
            else:
                self.config.logger.debug(
                    f"Word {index} has invalid text input: '{word}'"
                )
                faulty_words.append(str(index))

        if valid_words:
            valid_text = (
                "Input Successful. The following words have been added: ["
                + ", ".join(valid_words.keys())
                + "]."
            )
            for word, chance in valid_words.items():
                self.genre_context.selected_genre.inspirational_words.append(
                    INSPIRATIONALWORD(text=word, chance=chance)
                )
            await update_db_objs(self.config, [self.genre_context.selected_genre])
            self.config.logger.debug(
                f"New words are generated for genre id: {self.genre_context.selected_genre.id}"
            )
        if faulty_words:
            faulty_text = (
                "The input fields did not contain or had an incorrect input format: ["
                + ", ".join(faulty_words)
                + "]."
            )

        await interaction.response.edit_message(
            content=valid_text + " " + faulty_text,
        )
        self.parent_view.stop()


class UpdateContentButtonView(discord.ui.View):
    """
    Button view class to update genre content with selected option.
    """

    def __init__(self, config: Configuration, genre_context: GenreContext):
        super().__init__()
        self.config = config
        self.genre_context = genre_context

    @discord.ui.button(
        label="Add Event to Genre",
        style=discord.ButtonStyle.blurple,
    )
    async def button_callback_add_event(
        self, button: discord.ui.button, _: discord.interactions.Interaction
    ):
        """
        Button callback if button selected to add new event to genre.
        """
        self.config.logger.trace("Select option to add new event to a genre.")
        add_event_to_genre = AddEventToGenreModal(self, self.config, self.genre_context)
        await button.response.send_modal(add_event_to_genre)
        await add_event_to_genre.wait()

    @discord.ui.button(
        label="Add words to Genre",
        style=discord.ButtonStyle.blurple,
    )
    async def button_callback_add_words(
        self, button: discord.ui.button, _: discord.interactions.Interaction
    ):
        """
        Button callback if button selected to add new inspirational words to genre.
        """
        self.config.logger.trace("Select option to add new words to a genre.")
        add_words_to_genre = AddWordsToGenreModal(self, self.config, self.genre_context)
        await button.response.send_modal(add_words_to_genre)
        await add_words_to_genre.wait()


async def update_genre_with_content(
    interaction: Interaction, config: Configuration
) -> None:
    """
    This function allows the user to update genre content.

    Args:
        interaction (Interaction): Discord interaction object
        config (Configuration): App configuration
    """
    genre_context = GenreContext()
    genre_context.available_genre = await get_active_genre(config)
    await single_genre_selection(interaction, config, genre_context)
    if genre_context.selected_genre is None:
        config.logger.trace(
            f"No genre available for the ID: {genre_context.selected_genre_id}"
        )
        return
    telling_view = UpdateContentButtonView(config, genre_context)
    await interaction.followup.send(view=telling_view, ephemeral=True)
    await telling_view.wait()
