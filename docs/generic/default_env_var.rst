Default env variable
==========================
The following list shows all default settings with their type and function. If basic 
settings are specified in the main application, these are replaced with the following settings.

==============================  =====  ============= ==================================== ================
Name                            Type   Value         Explanation                          Location 
==============================  =====  ============= ==================================== ================
TT_GEN_REQ_REQUEST_TIMEOUT      int    30            Time to about requests               generic requests
TT_WATCHER_LOG_FILE_PATH        str    files/app.log Path for logging file                watcher
TT_WATCHER_LOG_LEVEL            str    INFO          Default log level                    watcher
==============================  =====  ============= ==================================== ================

.. note::

   It is not necessary to write all the letters in uppercase. The library automatically converts it.
   However, it is recommended to use uppercase letters for better readability.