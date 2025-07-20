"""Utilities exposing important project directories."""

from dataclasses import dataclass
from pathlib import Path

import LightWave2D


@dataclass(frozen=True)
class ProjectDirs:
    """Container for relevant LightWave2D directories."""

    root_path: Path = Path(LightWave2D.__path__[0])
    project_path: Path = root_path.parents[0]
    doc_path: Path = project_path / "docs"
    doc_css_path: Path = doc_path / "source/_static/default.css"


paths = ProjectDirs()

__all__ = ["root_path", "project_path", "doc_path", "doc_css_path"]

# Public shortcuts for convenience
root_path = paths.root_path
project_path = paths.project_path
doc_path = paths.doc_path
doc_css_path = paths.doc_css_path


if __name__ == "__main__":
    for path_name in __all__:
        path = globals()[path_name]
        print(path)
        assert path.exists(), f"Path {path_name} does not exist"
