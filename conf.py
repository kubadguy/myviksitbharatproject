# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# --- Setup for Code Autodoc (crucial for projects like Antraticks) ------------------
import os
import sys
# Add the project's root directory to the path so Autodoc can find your code
sys.path.insert(0, os.path.abspath('..'))
# -----------------------------------------------------------------------------------

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'twin connections'
copyright = '2025, Kushaal Srinandan Reddy Bandi'
author = 'Kushaal Srinandan Reddy Bandi'
release = '0.0.2'
# The full version, including alpha/beta/rc tags
version = release 


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    # Core Extensions
    'myst_parser',          # Enables using Markdown (.md) files
    'sphinx_rtd_theme',     # Read the Docs theme (highly recommended)

    # Documentation & Code Extensions
    'sphinx.ext.autodoc',   # Automatically document Python code from docstrings
    'sphinx.ext.napoleon',  # Supports Google/NumPy style docstrings
    'sphinx.ext.viewcode',  # Links source code from documentation

    # Utility Extensions
    'sphinx.ext.todo',      # Support for todo notes
    'sphinx.ext.linkcheck', # Checks all external links for 404s
]

# Configure the Markdown parser
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "html_image",
    "replacements",
    "linkify",
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Specify the file suffixes Sphinx should look for
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# **IMPORTANT CHANGE**: Using the Read the Docs theme
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Set the logo and favicon
# html_logo = "_static/your_logo.png"
# html_favicon = "_static/your_favicon.ico"

# -- Options for Autodoc -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'private-members': False,
    'special-members': False,
    'inherited-members': False,
    'show-inheritance': True,
}