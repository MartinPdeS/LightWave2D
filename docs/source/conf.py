"""LightWave2D documentation configuration."""

import os
import sys
from pathlib import Path

from MPSPlots.styles import use_mpsplots_style
from sphinx_gallery.sorting import FileNameSortKey
from martinpdes_docs import configure


ROOT = Path(__file__).resolve().parents[2]
# Prefer the installed package built by the documentation workflow so the
# compiled extension modules are available to autodoc and gallery examples.
sys.path.append(str(ROOT))

project = "LightWave2D"
package = "LightWave2D"
repository = "MartinPdeS/LightWave2D"
version = os.getenv("tag", "latest")


def reset_mpl(gallery_conf, fname):
    """Apply the project plotting style before each gallery example."""
    use_mpsplots_style()


examples_files = ["scattering", "detector", "extra"]

globals().update(
    configure(
        project=project,
        package=package,
        repository=repository,
        version=version,
        logo="_static/logo.png",
        favicon="_static/lightwave2d-favicon.svg",
        sphinx_gallery_conf={
            "examples_dirs": [f"../examples/{name}" for name in examples_files],
            "gallery_dirs": [f"gallery/{name}" for name in examples_files],
            "within_subsection_order": FileNameSortKey,
            "reset_modules": reset_mpl,
            "abort_on_example_error": True,
        },
        html_theme_options={
            "logo": {
                "text": "",
                "image": "_static/logo.png",
            },
        },
    )
)

extensions += ["sphinx.ext.mathjax", "sphinx.ext.autosectionlabel", "numpydoc"]
html_css_files += ["layout.css"]
html_context["doc_path"] = "docs/source"
html_context["default_mode"] = "dark"
