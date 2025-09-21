from datetime import datetime, timezone

import discord
from discord import Interaction

from .configuration import Configuration
from .db import GAME, GENRE, TALE
from .db import get_all_genre, get_genre_double_cond, process_player, update_db_objs


class GenreSelect(discord.ui.Select):
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
    def __init__(self, config, game_data: dict, genres: list[GENRE]):
        super().__init__()
        self.add_item(GenreSelect(config, game_data, genres))


class UserSelectView(discord.ui.View):
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
        self.game_data["user"] = select.values
        await interaction.response.edit_message(
            content="You have chosen the player for the new game.",
        )
        self.stop()


class GameInfoModal(discord.ui.Modal, title="Enter the playing hours for each player"):
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
        self.game_data["game_name"] = self.game_name_input.value
        await interaction.response.edit_message(
            content="All other game information has been entered.",
        )


async def collect_all_game_contexts(interaction: Interaction, config: Configuration) -> dict:
    try:

        game_data = {}
        user_view = UserSelectView(config, game_data)
        await interaction.response.send_message(
            "Please select all players for the new story.",
            view=user_view,
            ephemeral=True,
        )
        await user_view.wait()

        genres = await get_all_genre(config)
        genre_view = GenreSelectView(config, game_data, genres)
        await interaction.followup.send(
            "Please select the genre for the new story.",
            view=genre_view,
            ephemeral=True,
        )
        await genre_view.wait()
        print(game_data)
        return game_data
    except Exception as err:
        print(err)


async def create_game(interaction: Interaction, config: Configuration):
    try:
        game_data = await collect_all_game_contexts(interaction, config)
        genre = await get_genre_double_cond(config, game_data["genre_id"])
        processed_user_list = await process_player(config, game_data["user"])
        tale = TALE(genre=genre)
        game = GAME(
            name=game_data["game_name"],
            start_date=datetime.now(timezone.utc),
            message_id=12345678, # TODO: Muss später auf Nullable True gesetzt werden, da erst die Nachricht erst am Ende aller Einstellungen geschrieben wird.
            tale=tale,
            users=processed_user_list
        )
        await update_db_objs(config, [game])

        # 5. Jedem User eine private Nachricht schreiben und einladen
    except Exception as err:
        print(err, type(err))


async def keep_telling(interaction: Interaction, config: Configuration):
    print("Keep telling")
