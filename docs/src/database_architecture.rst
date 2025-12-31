Database architecture
==========================
This document provides an overview of the database architecture used in the project, including the main entities, their relationships, and the workflow for handling Discord commands.

Context classes
----------------------

.. mermaid ::
    erDiagram
        INSPIRATIONALWORD }|--|| GENRE : "N:1"
        EVENT }|--|| GENRE : "N:1"
        GENRE }|--|| TALE : "N:1"
        TALE ||--|{ STORY : "1:N"
        GAME ||--|| TALE : "1:1"
        GAME }|--|{ UserGameCharacterAssociation : "N:M"
        CHARACTER ||--|| UserGameCharacterAssociation : "1:1"
        USER }|--|{ UserGameCharacterAssociation : "N:M"
        STORY ||--|{ MESSAGE : "1:N"

        style GENRE fill:#f9f,stroke:#333,stroke-width:4px
        style CHARACTER fill:#f9f,stroke:#333,stroke-width:4px
        style INSPIRATIONALWORD fill:#f9f,stroke:#333,stroke-width:4px
        style EVENT fill:#f9f,stroke:#333,stroke-width:4px
        style UserGameCharacterAssociation fill:#AB82FF,stroke:#333,stroke-width:4px
        
        UserGameCharacterAssociation {
            int id
            int game_id
            int user_id
            int character_id
            datetime request_date
            datetime end_date
        }
        CHARACTER {
            int id
            string name
            int age
            string background
            string description
            string pos_trait
            string neg_trait
            string summary
            boolean alive
            datetime start_date
            datetime end_date
            int user_id
        }
        GAME {
            int id
            string name
            string description
            GameStatus status
            datetime start_timestamp
            datetime end_timestamp
            int message_id
            int channel_id
            int tale_id
        }
        TALE {
            string id
            int genre_id
        }
        STORY {
            string id
            string request
            string response
            string summary
            StoryType story_type
            datetime timestamp
            boolean discarded
            int tale_id
        }
        USER {
            string id
            string name
            string dc_id
        }
        GENRE {
            string id
            string name
            string storytelling_style
            string atmosphere
            string language
            boolean active
        }
        INSPIRATIONALWORD {
            string id
            string text
            int chance
            int genre_id
        }
        EVENT {
            string id
            string text
            int chance
            int genre_id
        }
        MESSAGE {
            string id
            int message_id
            int story_id
        }

.. note::
    The tables in pink can be customized, modified, or expanded through imports. This allows the stories to be individually tailored to the needs of the players, creating new and exciting stories every time.

.. note::
    The table in purple serves as a association table to manage the N:M relationships.