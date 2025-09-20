import discord
from discord import Interaction
from .configuration import Configuration
from .db import get_all_genre, get_genre_double_cond
from .db import GENRE


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
        await interaction.response.edit_message(
            content=(
                "All general entries for a new game have been made. "
                "Now it's up to the players to get involved."
            )
        )
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


async def create_game(interaction: Interaction, config: Configuration):
    try:
        # 1. User auswählen (user select)
        game_data = {}
        user_view = UserSelectView(config, game_data)
        await interaction.response.send_message(
            "Please select all players for the new story.",
            view=user_view,
            ephemeral=True,
        )
        await user_view.wait()
        # 2. Genre auswählen (option select)
        genres = await get_all_genre(config)
        genre_view = GenreSelectView(config, game_data, genres)
        await interaction.followup.send(
            "Please select the genre for the new story.",
            view=genre_view,
            ephemeral=True,
        )
        await genre_view.wait()
        print(game_data)
        # 3. Tale, Game erstellen
        # 4. Jedem User eine private Nachricht schreiben und einladen
    except Exception as err:
        print(err)


async def keep_telling(interaction: Interaction, config: Configuration):
    print("Keep telling")
