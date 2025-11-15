Main schedule
==========================

The following diagram shows the start of the generic main with the calls in the 
configuration and the logger.

.. mermaid ::
    graph TD
    A[Program Start] --> B[Load default.env]
    B --> C[Load .env with override parameters]
    C --> D[Create Configuration]
    D --> E[Write local configurations]
    E --> F[Initialize Watcher]
    F --> G[Program Execution]