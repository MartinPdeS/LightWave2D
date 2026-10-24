# Contributing to LightWave2D

Thank you for improving LightWave2D. Focused bug fixes, validated numerical
features, documentation corrections, and example contributions are welcome.

## Development setup

LightWave2D requires Python 3.10 or newer, CMake 3.20 or newer, a C++20
compiler, and pybind11. CMake must be able to find an OpenMP runtime; install
`libomp` on macOS before configuring a native build.

```bash
make editable
make test
```

After changing native C++ sources, rebuild the editable installation before
testing. Do not hand-edit `LightWave2D/_version.py`; the shared release helper
maintains it alongside explicit project metadata.

## Contribution expectations

- Add tests for every public behaviour change, including numerical validation
  where an analytical or independently computed reference is available.
- Exercise public Python APIs rather than only private extension modules.
- Keep physical units explicit at public boundaries and document numerical
  assumptions, stability limits, and boundary conditions.
- Add NumPy-style docstrings for public Python APIs and docstrings for bound
  native classes.
- Keep documentation-gallery examples small enough for automated builds.
- Do not commit native build products, generated documentation, caches, or
  Python bytecode.

Run the relevant focused tests first, then the project checks before opening a
pull request:

```bash
make quality
make test
make release-check
```

## Releases

Release tags use `vMAJOR.MINOR.PATCH`. `make tag VERSION=vX.Y.Z` regenerates
the source version file, creates a release commit, and creates an annotated
tag without pushing. `make release patch`, `make release minor`, and
`make release major` derive the next tag and push the release commit and tag.

## Shared release versioning

Versions are explicit in `[project].version`; builds never derive versions from
Git. Install the pinned release tool in the interpreter used by Make:

```sh
python -m pip install "martinpdes-maintenance==0.2.2"
make release-check PYTHON=python
```

The `release` extra declares the same tool. The scripts in `tools/` delegate to
it, and `[tool.mps-maintenance]` declares the package's release files. Use
`python tools/release_tag.py vX.Y.Z --dry-run` to preview changes from a clean,
full checkout. The tool aligns configured metadata, commits, and creates an
annotated tag; it never pushes. Existing Makefile publishing shortcuts retain
their push behavior. Fetch remote tags first. With no release tags, `next` uses
the explicit project version as its starting point.
