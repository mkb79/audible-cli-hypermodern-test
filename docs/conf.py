"""Sphinx configuration."""
project = "Audible Cli Hypermodern Test"
author = "mkb79"
copyright = "2023, mkb79"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "myst_parser",
]
autodoc_typehints = "description"
html_theme = "furo"
