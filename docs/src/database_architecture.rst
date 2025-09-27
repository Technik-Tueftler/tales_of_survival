Database architecture
==========================
This document provides an overview of the database architecture used in the project, including the main entities, their relationships, and the workflow for handling Discord commands.

Context classes
----------------------

.. mermaid ::
    erDiagram
        CHARACTER }|--|| USER : "N:1"
        USER }|--|{ GAME : "N:M"
        GAME ||--|| TALE : "1:1"
        TALE ||--|{ STORY : "1:N"
        TALE ||--|| GENRE : "1:1"
        InspirationalWords }|--|| GENRE : "N:1"
        EVENT }|--|| GENRE : "N:1"
        style GENRE fill:#f9f,stroke:#333,stroke-width:4px
        style CHARACTER fill:#f9f,stroke:#333,stroke-width:4px
        style InspirationalWords fill:#f9f,stroke:#333,stroke-width:4px
        style EVENT fill:#f9f,stroke:#333,stroke-width:4px
        CHARACTER {
            string id
            string name
            int age
            string background
            string description
            string pos_trait
            string neg_trait
            string summary
            boolean alive
        }
        GAME {
            string id
            string name
            string status
            datetime start_timestamp
            datetime end_timestamp
            int message_id
            int channel_id
        }
        TALE {
            string id
            string language
        }
        STORY {
            string id
            string request
            string response
            string summary
            StoryType story_type
        }
        USER {
            string id
            string dc_id
            string name
        }
        GENRE {
            string id
            string name
            string storytelling_style
            string atmosphere
        }
        InspirationalWords {
            string id
            string text
            int chance
        }
        EVENT {
            string id
            string text
            int chance
        }

.. note::
    The tables in pink can be customized, modified, or expanded through imports. This allows the stories to be individually tailored to the needs of the players, creating new and exciting stories every time.
