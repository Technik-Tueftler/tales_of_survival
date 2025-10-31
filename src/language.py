"""
Module to handle language localization.
"""
import yaml

def load_locale(locale: str) -> dict:
    """
    Function loads the selected language file and returns the content as a dictionary.

    Args:
        locale (str): Function to load the locale file

    Returns:
        dict: Loaded locale data
    """
    if locale == "de":
        with open("lang_de.yml", "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    else:
        with open("lang_en.yml", "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    # TODO: Kann komplett gelöscht werden, die Sprache wird über das Genre geladen und ausgesucht. Deshalb können die prompts einfach in den Constants geschrieben werden. Der Rest bleibt alles in englisch. Die Frage ist, muss ich die prompts überhaupt in englisch oder deutsch unterscheiden muss?        # context = {
        #     "genre_status": (
        #         config.locale["successful"]
        #         if result_genre.success
        #         else config.locale["unsuccessful"]
        #     ),
        #     "genre_number": result_genre.import_number,
        #     "char_status": (
        #         config.locale["successful"]
        #         if result_character.success
        #         else config.locale["unsuccessful"]
        #     ),
        #     "char_number": result_character.import_number,
        # }
        # message = config.locale["import_message"].format(**context)
