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
