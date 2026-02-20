watcher
==========================

.. automodule:: src.tetue_generic.watcher
    :members:
    :exclude-members: model_config


Initialization function
=======================
The initialization process is performed by the :func:`src.tetue_generic.watcher.init_logging` function. This function performs the following tasks:

Procedure for the initialization process
----------------------------------------

    1. Removes any existing log handlers.  
    2. Configures file logging with rotation and a size of 100MB.  
    3. Sets up console logging with color output

Log levels
----------
The following log levels are available:

   * TRACE
   * DEBUG
   * INFO
   * SUCCESS
   * WARNING
   * ERROR
   * CRITICAL
