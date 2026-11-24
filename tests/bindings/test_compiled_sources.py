"""Regression tests for compiled source geometry and validation."""

import numpy as np
import pytest
from TypedUnit import ureg

from LightWave2D import source
from LightWave2D.experiment import Experiment
from LightWave2D.grid import Grid


def test_compiled_point_geometry_indexes():
    geometry = source.PointGeometry(3, 4)
    assert np.array_equal(geometry.indexes, np.array([[3, 4]], dtype=np.int64))


def test_compiled_line_geometry_matches_bresenham_indexes():
    geometry = source.LineGeometry(0, 0, 3, 4)
    expected = np.array([[0, 0], [1, 1], [1, 2], [2, 3], [3, 4]], dtype=np.int64)
    assert np.array_equal(geometry.indexes, expected)


@pytest.mark.parametrize("geometry", [source.PointGeometry, source.LineGeometry])
def test_compiled_source_geometry_rejects_negative_indexes(geometry):
    arguments = (-1, 0) if geometry is source.PointGeometry else (-1, 0, 1, 1)
    with pytest.raises(ValueError):
        geometry(*arguments)


def test_python_sources_use_compiled_geometry_indexes():
    grid = Grid(
        resolution=1 * ureg.micrometer,
        size_x=10 * ureg.micrometer,
        size_y=5 * ureg.micrometer,
    )
    experiment = Experiment(grid=grid)
    point_source = experiment.add_point_source(
        wavelength=1.55 * ureg.micrometer,
        position=("center", "center"),
        amplitude=1.0,
    )
    line_source = experiment.add_line_source(
        wavelength=1.55 * ureg.micrometer,
        position_0=("left", "bottom"),
        position_1=("right", "top"),
        amplitude=1.0,
    )

    assert point_source._slc.shape == (1, 2)
    assert line_source._slc[0, 0] == 0
    assert np.array_equal(line_source._slc[-1], np.array([grid.n_x - 1, grid.n_y - 1]))


def test_compiled_wave_source_validates_array_lengths():
    indexes = np.array([[0, 0]], dtype=np.int64)
    with pytest.raises(ValueError):
        source.MultiWavelength(
            np.array([1.0, 2.0]),
            np.array([1.0]),
            np.array([0.0]),
            indexes,
        )
