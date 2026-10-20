# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.coverage', 'sphinx.ext.napoleon']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_themes"]

# -- Project information -----------------------------------------------------

project = 'etee Python API'
author = 'Pilar Zhang Qiu, Dimitri Chikhladze'
copyright = '2022, TG0'

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.

html_permalinks_icon = '<span>#</span>'

# Theme options
html_theme = 'sphinx_rtd_theme'

html_theme_options = {
    'logo_only': True,
    'prev_next_buttons_location': 'bottom',
    'style_nav_header_background': 'black',
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 3,
}

html_logo = "images/api_logo_transp-white.png"


# Favicon
html_favicon = "images/etee_api_favicon_black.png"

# Sidebar HTML pages to be included
# Use the theme's default sidebar templates and the documentation toctree.

# Theme overrides for custom CSS
def setup(app):
    app.add_css_file('theme_overrides.css')

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Path to python package, used by Sphinx Autodoc
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

html_baseurl = 'https://eteexr.github.io/etee-Python-API/'
