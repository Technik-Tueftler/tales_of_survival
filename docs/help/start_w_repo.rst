Starting project
================
This page will show you how to start with the template repository. The following steps
guide you from downloading the repository to create the virtual environment and install
the necessary packages.

1. Start project from template repository
    Go to https://github.com/Technik-Tueftler/TeTueGeneric and click **Create a new repository**.

    .. image:: ../images/start_from_template.png
        :width: 400
        :alt: Button to create a new repository from template

2. Clone the repository
    Clone your new repository to your local machine. You can use VS Code to clone the repository.

    .. image:: ../images/clone_repo_in_vs.png
        :width: 400
        :alt: Clone repository in VS Code


3. Create virtual environment
    Create a virtual environment in the root directory of the repository. You can use VS Code to create the virtual environment.

    .. image:: ../images/create_venv_in_vs.png
        :width: 400
        :alt: Create venv in VS Code

4. Install necessary packages
    Install the necessary packages from the requirements.txt file.

    .. code-block:: bash

        pip install -r requirements.txt

5. Update project information
    Update the project information in the **docs/conf.py** file. You can change project
    name, author, and other information.

6. Update repository information
    Update the project information in the **src/__init__.oy** file. You can change repository
    name and version. This is also the place where youu incement the version number if you
    make changes to the code and release patches, bug fixes or new features.

7. Update README.md
    Update the **README.md** file with the project information. You can add a description of the
    project, installation instructions, and usage information. Or only a link to the documentation.
