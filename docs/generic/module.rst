Adding a module
==========================
This site explains how to create a new module, both for the generic part and for the application.

The following illustration shows the structure of the project:

.. code-block:: rst

   Application
    ├── src
    │   ├── __init__.py
    │   ├── db.py
    │   └── tetue_generic
    │       ├── __init__.py
    │       └── watcher.py
    └── main.py

Generic
-------
The watcher module with new functions should be added to the generic folder.

1. Add new file *watcher.py* in **tetue_generic** directory
2. Add import for watcher in *__init__.py* in **src** directory

.. code-block:: python

    from .tetue_generic.watcher import *

3. Now the functions in *watcher.py* are available in *main.py*

Application
-----------

The db module with new functions should be added to the app folder.

1. Add new file *db.py* in **src** directory
2. Add import for db in *__init__.py* in **src** directory

.. code-block:: python

    from .db import *

3. Now the functions in *db.py* are available in *main.py* with

.. code-block:: python

    import src
    src.new_func_from_db()
