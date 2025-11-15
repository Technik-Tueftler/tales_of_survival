Discord command workflow
==========================
This document provides an overview of discord commands and how they are designed to interact with database and user inputs for process the game.

Command keep_telling
------------------------
This command is used to continue the story in an ongoing game. It involves several steps, including selecting a game, choosing the type of story input (event or text), and updating the story input in the database.

.. mermaid ::
    flowchart TD
        A[Recognized command] --> | Create object:
        story-input | B[(Database)]
        
        B --> | fetch ID | C[[Game
        select-view]]

        C --> | Game selected | D[[Story type
        button-view]]
        
        D --> | Event | E[Select random
        event]
        
        E --> F[Update object:
        story-input]
        
        D --> | Story | G[[input
        text-view]]
        
        G --> | input empty | H[Select random
        inspi word]
        
        H --> F
        G --> | text input | F