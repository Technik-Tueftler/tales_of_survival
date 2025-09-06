Database architecture
==========================


Context classes
----------------------

.. mermaid ::
    erDiagram
        CHARACTER }|--|| PLAYER : "N:1"
        PLAYER }|--|{ GAME : "N:M"
        GAME ||--|| TALE : "1:1"
        TALE ||--|{ STORY : "1:N"
        PLAYER }|--||USER : "N:1"
        TALE ||--|| GENRE : "1:1"
        style GENRE fill:#f9f,stroke:#333,stroke-width:4px
        CHARACTER {
            string id
            string name
            int alter
            string background
            string description
            string pos_trait
            string neg_trait
            string summary
        }
        PLAYER {
            string id
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
            string text
            string type
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

.. note::
    Die tabellen in rosa können durch imports angepasst, verändert oder erweitert werden. So kann eine individuelle Anpassung der Geschichten an die Bedürfnisse der Spieler vorgenommen werden und so immer neue und spannende Geschichten entstehen.