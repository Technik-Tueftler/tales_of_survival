import discord
from discord import Interaction
from .configuration import Configuration
from .db import get_all_genre
from .db import GENRE

class GenreSelectView(discord.ui.View):
    def __init__(self, config, game_data: dict, genre: list[GENRE]):
        super().__init__()
        self.config = config
        self.game_data = game_data



class UserSelectView(discord.ui.View):
    def __init__(self, config, game_data: dict, genre: list[GENRE]):
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
        await interaction.response.send_message("Finish")
        self.stop()


async def create_game(interaction: Interaction, config: Configuration):
    try:
        # 1. User auswählen (user select)
        game_data = {}
        genre = await get_all_genre(config)
        user_view = UserSelectView(config, game_data, genre)
        await interaction.response.send_message(
            "Bitte alle Mitspieler auswählen",
            view=user_view,
            ephemeral=True,
        )
        await user_view.wait()

        # 2. Genre auswählen (option select)
        # 3. Tale, Game erstellen
        # 4. Jedem User eine private Nachricht schreiben und einladen
    except Exception as err:
        print(err)


async def keep_telling(interaction: Interaction, config: Configuration):
    print("Keep telling")
