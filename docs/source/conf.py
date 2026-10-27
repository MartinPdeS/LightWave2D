"""LightWave2D documentation configuration."""

import sys
from pathlib import Path

from MPSPlots.styles import use_mpsplots_style
from martinpdes_docs import configure


ROOT = Path(__file__).resolve().parents[2]
# Documentation is built from the installed wheel. Remove the checkout from
# import resolution so its pure-Python package cannot shadow compiled modules
# installed by the documentation workflow.
source_paths = {ROOT.resolve(), (ROOT / "LightWave2D").resolve()}
sys.path[:] = [
    entry for entry in sys.path if entry and Path(entry).resolve() not in source_paths
]

project = "LightWave2D"
package = "LightWave2D"
repository = "MartinPdeS/LightWave2D"


def reset_mpl(gallery_conf, fname):
    """Apply the project plotting style before each gallery example."""
    use_mpsplots_style()


examples_files = ["scattering", "detector", "extra"]

globals().update(
    configure(
        project=project,
        package=package,
        version="auto",
        repository=repository,
        logo="_static/logo.png",
        favicon="_static/lightwave2d-favicon.svg",
        prefer_installed_package=True,
        gallery_sections=examples_files,
        gallery_options={
            "reset_modules": reset_mpl,
            "abort_on_example_error": True,
        },
        logo_text="",
        html_css_files=["layout.css"],
    )
)
