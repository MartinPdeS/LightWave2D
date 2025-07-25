#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from sphinx_gallery.sorting import FileNameSortKey
from MPSPlots.styles import use_mpsplots_style
from pathlib import Path
import LightWave2D
from LightWave2D.directories import doc_css_path


package_name = "LightWave2D"
version = LightWave2D.__version__

current_dir = Path(".")

sys.path.append(str(current_dir.resolve()))


def setup(app):
    app.add_css_file(str(doc_css_path))


autodoc_mock_imports = [
    'numpy',
    'matplotlib',
    'numpydoc',
]


project = package_name
copyright = '2024, Martin Poinsinet de Sivry-Houle'
author = 'Martin Poinsinet de Sivry-Houle'

extensions = [
    'sphinx.ext.mathjax',
    'sphinx_gallery.gen_gallery',
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.intersphinx',
]

# Napoleon settings for docstrings
napoleon_google_docstring = False
napoleon_numpy_docstring = True

html_logo = "_static/thumbnail.png"
html_favicon = "_static/thumbnail.png"


def reset_mpl(gallery_conf, fname):
    use_mpsplots_style()


examples_files = [
    'scattering', 'detector', 'extra'
]

sphinx_gallery_conf = {
    "examples_dirs": ['../examples/' + f for f in examples_files],
    "gallery_dirs": ['gallery/' + f for f in examples_files],
    'image_scrapers': ('matplotlib'),
    'ignore_pattern': '/__',
    'filename_pattern': r'.*\.py',
    'plot_gallery': True,
    'thumbnail_size': [600, 600],
    'download_all_examples': False,
    'reset_modules': reset_mpl,
    'line_numbers': False,
    'remove_config_comments': True,
    'capture_repr': ('_repr_html_', '__repr__'),
    'nested_sections': True,
    'within_subsection_order': FileNameSortKey,
}


autodoc_default_options = {
    'members': False,
    'members-order': 'bysource',
    'undoc-members': False,
    'show-inheritance': True,
}

autosectionlabel_prefix_document = True
numpydoc_show_class_members = False
add_module_names = False

source_suffix = '.rst'
master_doc = 'index'
language = 'en'
highlight_language = 'python3'
html_theme = "pydata_sphinx_theme"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

exclude_trees = []
# default_role = "autolink"
pygments_style = "sphinx"

# -- Sphinx-gallery configuration --------------------------------------------
major, minor = version[:2]
binder_branch = f"v{major}.{minor}.x"

html_theme_options = dict()

html_theme_options['logo'] = dict(text=package_name, image="_static/thumbnail.png")
html_theme_options["show_nav_level"] = 0

html_theme_options.update({
    "icon_links": [
        {
            "name": "GitHub",
            "url": f"https://github.com/MartinPdeS/{package_name}",
            "icon": "fa-brands fa-github",
        },
        {
            "name": "PyPI",
            "url": f"https://pypi.org/project/{package_name}/",
            "icon": "fa-solid fa-box",
        },
        {
            "name": "Anaconda",
            "url": f"https://anaconda.org/MartinPdeS/{package_name}",
            "icon": "fa-brands fa-python",
        },
    ],
    "navbar_align": "left",
    "navbar_end": ["version-switcher", "navbar-icon-links"],
    "show_prev_next": False,
    "show_version_warning_banner": True,
    # Footer
    "footer_start": ["copyright"],
    "footer_end": ["sphinx-version", "theme-version"],
    # Other
    "pygments_light_style": "default",
    "pygments_dark_style": "github-dark",
}
)

current_version = os.getenv("tag", "latest")

html_theme_options["switcher"] = dict(
    json_url=f"https://raw.githubusercontent.com/MartinPdeS/{package_name}/documentation_page/version_switcher.json",
    version_match=current_version,
)

htmlhelp_basename = f'{package_name}doc'

latex_elements = {}


latex_documents = [
    (master_doc, f'{package_name}.tex', f'{package_name} Documentation',
     'Martin Poinsinet de Sivry-Houle', 'manual'),
]

man_pages = [
    (master_doc, 'supymode', f'{package_name} Documentation',
     [author], 1)
]

texinfo_documents = [
    (master_doc, package_name, f'{package_name} Documentation',
     author, package_name, 'One line description of project.',
     'Miscellaneous'),
]

epub_title = project

html_static_path = ['_static']
templates_path = ['_templates']
html_css_files = ['default.css']
epub_exclude_files = ['search.html']

# -
