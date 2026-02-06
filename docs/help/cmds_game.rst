Subcommand game
==========================
All subcommands related to game are listed and described here.

.. note::
    A select view is created with this commands. Please note :ref:`limitations_for_selects` 
    for restrictions on display.

Overview
-----------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Command
     - Description
   * - ``create``
     - Subcommand to create a new game and invite players.
   * - ``setup``
     - Subcommand to start a new game or change its status to pause, running or stopped.
   * - ``reset``
     - Subcommand to reset a freshly started game.
   * - ``finish``
     - Subcommand to complete a stopped game and write the book.


Reset game
-----------------
After a game has been started (from created to running), the game master must enter a prompt 
to create the start of the tale. If the first part of the story does not meet the requirements, 
this command allows you to start again and generate the start of the Tale. This is possible 
until the first part of the story has been told in the tale (using the keep_telling command).

.. warning::
   After the first part of the tale has been told using the keep_telling command, it is no 
   longer possible to recreate or delete individual parts of the story.