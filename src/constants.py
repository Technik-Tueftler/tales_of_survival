"""
Constants for organizing various fixed values used across the application.
"""

DEFAULT_THUMBNAIL_URL: str = (
    "https://raw.githubusercontent.com/Technik-Tueftler/tales_of_survival/refs/heads/main/files/"
)
"""Default folder URL for thumbnail images used in embeds."""

DEFAULT_TALE_THUMBNAIL: str = "icon_tale_small.png"
"""Default name for tale thumbnail image used in embeds."""

DEFAULT_CHARACTER_THUMBNAIL: str = "icon_character_small.png"
"""Default name for character thumbnail image used in embeds."""

DEFAULT_EVENT_THUMBNAIL: str = "icon_event_small.png"
"""Default name for event thumbnail image used in embeds."""

DEFAULT_QUESTION_THUMBNAIL: str = "icon_question_small.png"
"""Default name for question thumbnail image used in embeds."""

DEFAULT_FINISH_THUMBNAIL: str = "icon_finish_small.png"
"""Default name for finish game thumbnail image used in embeds."""

PROMPT_MAX_WORDS_DESCRIPTION: int = 200
"""Maximum number of words for describing the world of the tale."""

PROMPT_MAX_WORDS_START: int = 600
"""Maximum number of words for the beginning of the tale."""

PROMPT_MAX_WORDS_END: int = 800
"""Maximum number of words for the end of the tale."""

PROMPT_MAX_WORDS_EVENT: int = 150
"""Maximum words for the prompt for the description."""

PROMPT_MAX_WORDS_FICTION: int = 300
"""Maximum number of words for an event."""

DC_MAX_CHAR_MESSAGE: int = 2000
"""Maximum number of characters for a message in Discord."""

DC_DESCRIPTION_MAX_CHAR: int = 100
"""Maximum number of characters for Discord input."""

DC_MODAL_INPUT_EVENT_TEXT_MAX_CHAR: int = 200
"""Maximum number of characters for event text in Discord modal input."""

DC_MODAL_INPUT_EVENT_TEXT_MIN_CHAR: int = 20
"""Minimum number of characters for event text in Discord modal input."""

DC_MODAL_INPUT_WORD_TEXT_MAX_CHAR: int = 20
"""Maximum number of characters for a word in Discord modal input."""

DC_MODAL_INPUT_WORD_TEXT_MIN_CHAR: int = 1
"""Minimum number of characters for a word in Discord modal input."""

DC_EMBED_DESCRIPTION: str = "A new story is being told!"
"""Default tale description in game embed."""

NEW_TALE_FIRST_PHASE_PROMPT_PART_1: str = (
    "Du bist ein Geschichtenerzähler für das Genre #GenreName. "
    "Schreibe ausschließlich in #GenreLanguage."
)
"""Prompt template for genre name and language in the first phase of a new tale."""

NEW_TALE_FIRST_PHASE_PROMPT_PART_2: str = (
    " Der Erzählstil soll #GenreStorytellingStyle sein."
)
"""Prompt template for storytelling style in the first phase of a new tale."""

NEW_TALE_FIRST_PHASE_PROMPT_PART_3: str = (
    " Die Atmosphäre der Geschichte ist #GenreAtmosphere."
)
"""Prompt template for atmosphere in the first phase of a new tale."""

NEW_TALE_FIRST_PHASE_PROMPT_PART_4: str = (
    " Beschreibe die Welt, in der die Menschen jetzt leben müssen. "
    "Maximal #MaxWords Wörter."
)
"""Prompt template for world description in the first phase of a new tale."""

NEW_TALE_SECOND_PHASE_PROMPT_MULTI_PART_1: str = (
    "Die Geschichte handelt von #NumberCharacters Charakteren. "
    "Füge keine neuen Charaktere hinzu, es sei denn, ein späterer Prompt beschreibt "
    "sie ausdrücklich. Hier sind die Charaktere:"
)
"""Prompt template for number of characters in the second phase of a new tale."""

NEW_TALE_SECOND_PHASE_PROMPT_MULTI_PART_2: str = (
    "Erzähle den Beginn der Geschichte mit maximal #MaxWords Wörtern. "
    "Die Charaktere treffen sich in der Stadt #City und beschließen, "
    "eine Gemeinschaft zu bilden."
)
"""Prompt template for story start in the second phase of a new tale. This is only 
used if no custom prompt is provided by the user."""

NEW_TALE_SECOND_PHASE_PROMPT_SINGLE_PART_1: str = (
    "Die Geschichte handelt von einem einzelnen Protagonisten. Füge keine "
    "neuen Charaktere hinzu, es sei denn, ein späterer Prompt beschreibt sie ausdrücklich. "
    "Hier ist die Zusammenfassung des Protagonisten: #CharacterSummary."
)
"""Prompt template for single character summary in the second phase of a new tale."""

NEW_TALE_SECOND_PHASE_PROMPT_SINGLE_PART_2: str = (
    "Erzähle den Beginn der Geschichte mit maximal #MaxWords Wörtern. "
    "Der Protagonist befindet sich in der Stadt #City, wo er versucht, zu überleben."
)
"""Prompt template for story start with single character in the second phase of a new tale.
This is only used if no custom prompt is provided by the user."""

EVENT_REQUEST_PROMPT: str = (
    "Erzähl den nächsten Teil der Geschichte auf Grundlage des folgenden Ereignisses: "
    + "#EventText. Passe das Ereignis inhaltlich so an, dass es zur aktuellen "
    + "Spieleranzahl passt. Wenn nur ein Spieler teilnimmt, gestalte das Ereignis so, "
    + "dass es sich ausschließlich auf diesen Spieler bezieht. Der Text darf maximal "
    + "#MaxWords Wörter umfassen und soll flüssig an die bisherige Handlung anschließen."
)
"""Prompt template for event description during story telling phase."""

FICTION_REQUEST_PROMPT: str = (
    "Schreibe die Geschichte weiter basierend auf dem folgenden Input: "
    + "#FictionText. Interpretiere den Input kontextabhängig – er kann "
    + "ein einzelnes Wort, ein Satz oder ein längerer Text sein. Passe "
    + "das Ereignis bei Bedarf an die aktuelle Spieleranzahl an; falls "
    + "nur ein Spieler vorhanden ist, kannst du das Geschehen auf diesen "
    + "beziehen. Der Text darf maximal #MaxWords Wörter umfassen."
)
"""Prompt template for fiction description during story telling phase."""

FINAL_REQUEST_PROMPT_USER: str = (
    "Schließe die Geschichte jetzt ab, basierend auf dem folgenden finalen Input: #FinalText. "
    "Interpretiere den Input kontextabhängig – er kann ein einzelnes Wort, ein Satz oder ein "
    "längerer Text sein – und behandle den vom User vorgegebenen Inhalt als absolute Priorität. "
    "Der Text darf außerdem enthalten, welche Stimmung das Ende haben soll (z.B. hoffnungsvoll, "
    "bittersüß, düster oder offen). Behandle diese Stimmungs‑Vorgabe als Neben‑Richtlinie, die "
    "nur dann greift, wenn sie nicht im Widerspruch zum eigentlichen Inhalt des Inputs steht."
    "Passe das Finale technisch an die aktuelle Spieleranzahl an; falls nur ein Spieler vorhanden "
    "ist, kannst du den Ausgang auf diese Person konzentrieren. Das finale Kapitel darf "
    "maximal #MaxWords Wörter umfassen und soll den bisherigen Handlungsstrang konsistent "
    "fortsetzen, ohne neue Hauptkonflikte zu beginnen.Forme den Schluss so, dass der Wille des "
    "Users im Text inhaltlich und stimmungsmäßig klar im Vordergrund steht, auch wenn dies "
    "leichte Abweichungen vom bisherigen Stil oder Ton bedeutet."
)
"""Prompt template for final story based on user input."""

FINAL_REQUEST_PROMPT: str = (
    "Schließe die Geschichte jetzt ab, basierend auf dem bisherigen Verlauf und dem aktuellen "
    "Kontext der Handlung. Gestalte das Finale so, dass alle bisherigen Hauptkonflikte gelöst "
    "oder klar eingeordnet werden, ohne neue zentrale Konflikte zu beginnen. Passe den Ausgang "
    "an die aktuelle Spieleranzahl an; falls nur ein Spieler vorhanden ist, kannst du den Fokus "
    "auf diese Person legen. Das finale Kapitel darf maximal #MaxWords Wörter umfassen und soll "
    "den bisherigen Stil und die Stimmung der Geschichte konsistent fortsetzen. Entscheide je "
    "nach Ton der bisherigen Handlung, ob das Ende eher hoffnungsvoll, bittersüß oder offen "
    "ausfällt, aber forme es zu einem klaren narrativen Abschluss."
)
"""Prompt template for final story."""
