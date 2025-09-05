Adding a configuration
==========================
This site explains how to create a new configuration, both for the generic part and for the application.

The following illustration shows the structure of the project:

.. code-block:: rst

   Application 
    ├── src
    │   ├── __init__.py
    │   ├── db.py
    │   ├── configuration.py
    │   └── tetue_generic
    │       ├── __init__.py
    │       └── watcher.py
    ├── default.env
    └── main.py

Generic
-------
Create a new module in the generic folder, e.g. ``gentester.py``. If a configuration is 
required for the new generic parts, the following must be created.

1. Create a configuration class in ``gentester.py``, customize delimiter and change the default value ``test_var``

.. code-block:: python

    import environ

    @environ.config(prefix="TEST_CONF")
    class GenTestConfiguration:
        """
        Configuration settings for test example.
        """

        request_timeout = environ.var(
            "test_var", help="This variable is just for testing purposes"
        )


2. Import the new configuration class in ``src/configuration.py``

.. code-block:: python

    from .tetue_generic.gentester import GenTestConfiguration

3. Add the new configuration variables to ``Configuration`` in ``src/configuration.py``

.. code-block:: python

    @environ.config(prefix="TT")
    class Configuration:
        """
        Configuration class for the entire application, grouping all sub-configurations.
        """
        gen_req = environ.group(GenReqConfiguration)
        watcher = environ.group(WatcherConfiguration)
        gentester = environ.group(GenTestConfiguration)

4. Add new configuration variables to *.env* with nested delimiter
.. code-block:: rst

    TT_TEST_CONF_TEST_VAR=example_value

Application
-----------

For the application, the configuration is created in the same way as for the generic part. For example, 
if a database configuration is required (``for src/db.py``), proceed the same ways as above.

Primary
-----------

If you need settings that are once again superordinate in the project, i.e. are not directly assigned 
to a module (user and name), these are specified and verified directly in the configuration class.

.. code-block:: python

    @environ.config(prefix="TT")
    class Configuration:
        """
        Configuration class for the entire application, grouping all sub-configurations.
        """
        test_value = environ.var("value", help="This is a value.")
        gen_req = environ.group(GenReqConfiguration)
        watcher = environ.group(WatcherConfiguration)
        gentester = environ.group(GenTestConfiguration)

The new variable is then added to *.env* as follows:

.. code-block:: rst

    TT_TEST_VALUE=example_value

.. note::

   It is not necessary to write all the letters in uppercase. The library automatically converts it.
   However, it is recommended to use uppercase letters for better readability.

Validation
----------
It is possible to validate configuration variables. The library ``environ`` supports this natively.
For further information, refer to official documentation of `environ`_.

.. _environ: https://environ-config.readthedocs.io/en/stable/index.html