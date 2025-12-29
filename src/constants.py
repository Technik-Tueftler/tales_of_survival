"""
Constants for organizing various fixed values used across the application.
"""

DEFAULT_TALE_THUMBNAIL_URL: str = (
    "https://raw.githubusercontent.com/Technik-Tueftler/tales_of_survival/refs/heads/main/files/thumbnail_tale.png"
)
"""Default URL for the tale thumbnail image used in embeds."""

DEFAULT_CHARACTER_THUMBNAIL_URL: str = (
    "https://raw.githubusercontent.com/Technik-Tueftler/tales_of_survival/refs/heads/main/files/thumbnail_character.png"
)
"""Default URL for character thumbnail image used in embeds."""

PROMPT_MAX_WORDS_DESCRIPTION: int = 200
"""Maximum number of words for describing the world of the tale."""

PROMPT_MAX_WORDS_START: int = 600
"""Maximum number of words for the beginning of the tale."""

PROMPT_MAX_WORDS_EVENT: int = 150
"""Maximum words for the prompt for the description."""

PROMPT_MAX_WORDS_FICTION: int = 300
"""Maximum number of words for an event."""

DC_MAX_CHAR_MESSAGE: int = 2000
"""Maximum number of characters for a message in Discord."""

DC_DESCRIPTION_MAX_CHAR: int = 100
"""Maximum number of characters for Discord input."""

DC_EMBED_DESCRIPTION: str = "A new story is being told!"
"""Default tale description in game embed."""

NEW_TALE_FIRST_PHASE_PROMPT_PART_1: str = (
    "Du bist ein Geschichtenerzähler für ein/e #GenreName. "
    + "Die Antworten nur in #GenreLanguage."
)
"""Prompt template for genre name and language in the first phase of a new tale."""

NEW_TALE_FIRST_PHASE_PROMPT_PART_2: str = (
    " Der Erzählstil sollte: #GenreStorytellingStyle sein."
)
"""Prompt template for storytelling style in the first phase of a new tale."""

NEW_TALE_FIRST_PHASE_PROMPT_PART_3: str = (
    " Die Atmosphäre der Geschichte ist: GenreAtmosphere."
)
"""Prompt template for atmosphere in the first phase of a new tale."""

NEW_TALE_FIRST_PHASE_PROMPT_PART_4: str = (
    "Beschreibe mir die Welt in der die Menschen jetzt "
    + "leben müssen mit maximal #MaxWords Wörter)"
)
"""Prompt template for world description in the first phase of a new tale."""

NEW_TALE_SECOND_PHASE_PROMPT_MULTI_PART_1: str = (
    "Es sind die nachfolgenden Charaktere (Anzahl: #NumberCharacters) in der Geschichte. "
    + "Achte darauf, dass du keine neuen Charaktere hinzufügst, außer es wird ausdrücklich "
    + "in einem neuen prompt beschrieben."
)
"""Prompt template for number of characters in the second phase of a new tale."""

NEW_TALE_SECOND_PHASE_PROMPT_MULTI_PART_2: str = (
    "Erzähl mir den Start der Geschichte (maximal #MaxWords Wörter) bei der sich "
    + "die Charaktere in einer Stadt namens #City treffen und beschließen eine "
    + "Gemeinschaft zu bilden."
)
"""Prompt template for story start in the second phase of a new tale. This is only 
used if no custom prompt is provided by the user."""

NEW_TALE_SECOND_PHASE_PROMPT_SINGLE_PART_1: str = (
    "In der Geschichte geht es um einen Protagonisten. Achte darauf, dass du keine "
    + "neuen Charaktere hinzufügst, außer es wird ausdrücklich in einem neuen prompt beschrieben."
    + "Um den folgende Charaktere geht es in der Geschichte: #CharacterSummary"
)
"""Prompt template for single character summary in the second phase of a new tale."""

NEW_TALE_SECOND_PHASE_PROMPT_SINGLE_PART_2: str = (
    "Erzähl mir den Start der Geschichte (maximal #MaxWords Wörter) bei der sich der "
    "Charakter in einer Stadt namens #City aufhält und dort versucht zu überleben."
)
"""Prompt template for story start with single character in the second phase of a new tale.
This is only used if no custom prompt is provided by the user."""

EVENT_REQUEST_PROMPT: str = (
    "Erzähl mir einen neuen Teil der Geschichte basierend auf dem folgenden Ereignis: "
    + "#EventText mit maximal #MaxWords Wörtern. Achte darauf, dass das Ereignis so "
    + "angepasst wird, dass es für ein Spieler ist, wenn nur ein Charakter in der Geschichte ist."
)
"""Prompt template for event description during story telling phase."""

FICTION_REQUEST_PROMPT: str = (
    "Schreibe die Geschichte weiter basierend auf dem folgenden Input: "
    + "#FictionText mit maximal #MaxWords Wörtern."
)
"""Prompt template for fiction description during story telling phase."""
