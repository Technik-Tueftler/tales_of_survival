import discord
from discord import Interaction
from .db import get_active_genre, deactivate_genre_with_id
from .file_utils import limit_text
from .configuration import Configuration, GenreContext


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


async def deactivate_genre(interaction: Interaction, config: Configuration):
    try:
        process_data = GenreContext()
        process_data.available_genre = await get_active_genre(config)

        if not await process_data.input_valid_genre():
            await interaction.response.send_message(
                "No active genre is available, please contact a Mod.",
                ephemeral=True,
            )
            return

        genre_select_view = GenreSelectView(config, process_data)
        await interaction.response.send_message(
            "Please select the genre you want to deactivate",
            view=genre_select_view,
            ephemeral=True,
        )
        await genre_select_view.wait()

        if process_data.selected_genre_id == 0:
            await interaction.followup.send(
                "No genre was selected, cancelling deactivation.",
                ephemeral=True,
            )
            return
        await deactivate_genre_with_id(config, process_data.selected_genre_id)
        await interaction.followup.send(
            "Genre is deactivated successfully.",
            ephemeral=True,
        )

    except Exception as err:
        print(type(err), err)
