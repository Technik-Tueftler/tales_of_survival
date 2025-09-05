# pylint: skip-file
import sys
import os
sys.path.insert(0, os.path.abspath("../"))

from src import __version__, __repository__

project = 'TeTueGeneric'
copyright = '2025, Technik Tueftler'
author = 'Technik Tueftler'
release = __version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon', # docstrings like google and NumPy
    'sphinx.ext.intersphinx', # for intersphinx_mapping
    'sphinx.ext.viewcode', # open code 
    'sphinx_copybutton', # add copy button in code view
    'sphinx_toolbox.more_autodoc.typehints', # use type hints
    'myst_parser', # for Markdown documentation
    'sphinxmermaid', # for Mermaid diagrams
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'loguru': ('https://loguru.readthedocs.io/en/stable/', None),
    'requests': ('https://requests.readthedocs.io/en/latest/', None),
    }

autodoc_member_order = 'bysource'

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

sphinxmermaid_mermaid_init = {
  'theme': 'base',
  'themeVariables': {
    'primaryColor': '#4CAF50',
    'primaryTextColor': '#FFFFFF',
    'primaryBorderColor': '#757575',
    'lineColor': '#B0BEC5',
    'secondaryColor': '#2196F3',
    'tertiaryColor': '#2196F3'
  }
}


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'pydata_sphinx_theme'
html_theme_options = {
    "icon_links": [
        {
            "name": "GitHub",
            "url": __repository__,
            "icon": "fa-brands fa-github",
            "type": "fontawesome",
        },
        {
            "name": "Twitch",
            "url": "https://www.twitch.tv/technik_tueftler",
            "icon": "fa-brands fa-twitch",
            "type": "fontawesome",
        },
        {
            "name": "Youtube",
            "url": "https://www.youtube.com/@technik_tueftler",
            "icon": "fa-brands fa-youtube",
            "type": "fontawesome",
        },
    ],
}
html_static_path = []
