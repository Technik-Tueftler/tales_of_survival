Database architecture
==========================


Context classes
----------------------

.. mermaid ::
    erDiagram
        CHARACTER ||--|| PLAYER : "1:1"
        USER }|--|{ GAME : "N:M"
        GAME ||--|| TALE : "1:1"
        TALE ||--|{ STORY : "1:N"
        USER ||--|{ PLAYER : "1:N"
        TALE ||--|| GENRE : "1:1"
        InspirationalWords }|--|| GENRE : "N:1"
        EVENT }|--|| GENRE : "N:1"
        STORY ||--|| STORYTYPE : "1:1"
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
        }
        PLAYER {
            string id
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
        STORYTYPE {
            string id
        }

.. note::
    Die tabellen in rosa können durch imports angepasst, verändert oder erweitert werden. So kann eine individuelle Anpassung der Geschichten an die Bedürfnisse der Spieler vorgenommen werden und so immer neue und spannende Geschichten entstehen.


Discord command workflow
------------------------

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