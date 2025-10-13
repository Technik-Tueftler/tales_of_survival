"""
Module to handle game creation and management
"""

from datetime import datetime, timezone
import asyncio
import discord
from discord import Interaction

from .configuration import Configuration
from .db import GAME, GENRE, TALE, USER, UserGameCharacterAssociation, CHARACTER
from .db import (
    get_all_genre,
    get_genre_double_cond,
    process_player,
    update_db_objs,
    get_user_with_games,
    get_available_characters,
    get_object_by_id,
)


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


class GameSelect(discord.ui.Select):
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


async def collect_all_game_contexts(
    interaction: Interaction, config: Configuration
) -> dict:
    """
    Function to collect all necessary game contexts from user interactions.

    Args:
        interaction (Interaction): Interaction object from Discord
        config (Configuration): App configuration

    Returns:
        dict: game data collected from user interactions
    """
    try:
        game_data = {"Valid": False}
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
        game_data["Valid"] = True
        return game_data
    except discord.Forbidden:
        config.logger.error("Cannot send message, permission denied.")
        return game_data
    except discord.HTTPException as err:
        config.logger.error(f"Failed to send message: {err}")
        return game_data
    except (TypeError, ValueError) as err:
        config.logger.error(f"General error occurred: {err}")
        return game_data
    except asyncio.TimeoutError as err:
        config.logger.error(f"Timeout error occurred: {err}")
        return game_data


async def send_game_information(
    interaction: Interaction,
    config: Configuration,
    game: GAME,
    genre: GENRE,
    users: list[USER],
) -> discord.Message:
    """
    Functions create and send a Discord message with game information to a channel.

    Args:
        interaction (Interaction): Interaction object from Discord
        config (Configuration): App configuration
        game (GAME): Game object
        genre (GENRE): Genre object from game
        users (list[USER]): All player of the game

    Returns:
        discord.Message: Discord message object
    """
    try:
        embed = discord.Embed(
            title=game.name,
            description=f"A new story is being told! (ID: {game.id})",
            color=discord.Color.green(),
        )
        embed.add_field(name="Genre", value=genre.name, inline=False)
        embed.add_field(name="Language", value=genre.language, inline=True)
        embed.add_field(name="Style", value=genre.storytelling_style, inline=True)
        embed.add_field(name="Atmosphere", value=genre.atmosphere, inline=True)
        embed.add_field(
            name="The Players:",
            value=", ".join([f"<@{user.dc_id}>" for user in users]),
            inline=False,
        )

        message = await interaction.followup.send(embed=embed)
        return message
    except discord.Forbidden:
        config.logger.error("Cannot send message, permission denied.")
    except discord.HTTPException as err:
        config.logger.error(f"Failed to send message: {err}")
    except (TypeError, ValueError) as err:
        config.logger.error(f"General error occurred: {err}")


async def inform_players(
    config: Configuration, users: list[discord.member.Member], message_link: str
):
    """
    Send a DM to each player to inform them about the new game.

    Args:
        config (Configuration): App configuration
        users (list[discord.member.Member]): All player of the game
        message_link (str): Link to the game information message
    """
    try:
        message = (
            "Hello #USERNAME, you have been invited to participate in "
            f"**Tales of Survival**. Check: {message_link}"
        )
        for user in users:
            temp_message = message.replace("#USERNAME", user.name)
            await user.send(temp_message)
    except discord.Forbidden:
        config.logger.error(f"Cannot send message to {user.name}, permission denied.")
    except discord.HTTPException as err:
        config.logger.error(f"Failed to send message to {user.name}: {err}")


async def create_dc_message_link(
    config: Configuration, message: discord.Message, interaction: Interaction
) -> str:
    """
    Function to create a link to a specific Discord message.

    Args:
        config (Configuration): App configuration
        message (discord.Message): General message object to collect ids
        interaction (Interaction): Last interaction to collect guild id

    Returns:
        str: Message link in the format
    """
    message_link = (
        f"https://discord.com/channels/{interaction.guild.id}"
        f"/{message.channel.id}/{message.id}"
    )
    config.logger.debug(f"Create message link: {message_link}")
    return message_link


async def create_game(interaction: Interaction, config: Configuration):
    """
    Create a new game based on user inputs from Discord interactions.

    Args:
        interaction (Interaction): Intgeraction object from Discord
        config (Configuration): App configuration
    """
    try:
        game_data = await collect_all_game_contexts(interaction, config)
        genre = await get_genre_double_cond(config, game_data["genre_id"])
        processed_user_list = await process_player(config, game_data["user"])
        tale = TALE(genre=genre)
        game = GAME(
            name=game_data["game_name"],
            start_date=datetime.now(timezone.utc),
            tale=tale,
        )
        await update_db_objs(config, [game])
        associations = [
            UserGameCharacterAssociation(game_id=game.id, user_id=user.id)
            for user in processed_user_list
        ]
        await update_db_objs(config, associations)
        message = await send_game_information(
            interaction, config, game, genre, processed_user_list
        )
        game.message_id = message.id
        game.channel_id = message.channel.id
        config.logger.debug(
            f"Update game informations: message id {game.message_id}, channel id {game.channel_id}"
        )
        await update_db_objs(config, [game])
        message_link = await create_dc_message_link(config, message, interaction)
        await inform_players(config, game_data["user"], message_link)

    except discord.Forbidden:
        config.logger.error("Cannot send message, permission denied.")
    except discord.HTTPException as err:
        config.logger.error(f"Failed to send message: {err}")
    except (TypeError, ValueError) as err:
        config.logger.error(f"General error occurred: {err}")
    except asyncio.TimeoutError as err:
        config.logger.error(f"Timeout error occurred: {err}")
    except KeyError as err:
        config.logger.error(f"Missing key in game data or for DB object: {err}")
    except Exception as err:
        print(err, type(err))


async def keep_telling(interaction: Interaction, config: Configuration): ...


async def select_character(interaction: Interaction, config: Configuration) -> None:
    """
    This function is the entry and schedule point to select and process a character selection.

    Args:
        interaction (Interaction): Interaction object from Discord
        config (Configuration): App configuration
    """
    try:
        request_data = {"user_dc_id": str(interaction.user.id)}
        await get_user_with_games(config, request_data)
        if request_data.get("game_association") is None:
            await interaction.response.send_message(
                "An error occurred while retrieving your games. Your not registered "
                "for any game. Please contact the admin.",
                ephemeral=True,
            )
            return
        game_view = GameSelectView(config, request_data)
        await interaction.response.send_message(
            "Please select the game to select your character.",
            view=game_view,
            ephemeral=True,
        )
        await game_view.wait()
        if request_data.get("game_association_id") is None:
            await interaction.followup.send(
                "You did not select a game. Please try again.",
                ephemeral=True,
            )
            return
        await get_available_characters(config, request_data)
        if request_data.get("available_character") is None:
            await interaction.followup.send(
                "No characters are available for selection. Please contact the admin.",
                ephemeral=True,
            )
            return
        character_view = CharacterSelectView(config, request_data)
        await interaction.followup.send(
            "Please select now the character for the game.",
            view=character_view,
            ephemeral=True,
        )
        await character_view.wait()
        if request_data.get("selected_character") is None:
            await interaction.followup.send(
                "You did not select a character. Please try again.",
                ephemeral=True,
            )
            return
        game_association = await get_object_by_id(
            config, UserGameCharacterAssociation, request_data["game_association_id"]
        )
        selected_character = await get_object_by_id(
            config, CHARACTER, request_data["selected_character"]
        )
        selected_character.user_id = game_association.user_id
        selected_character.start_date = datetime.now(timezone.utc)
        game_association.character_id = int(request_data["selected_character"])
        await update_db_objs(config, [game_association, selected_character])

    except Exception as err:
        print(err, type(err))
