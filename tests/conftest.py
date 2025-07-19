import pytest
from LightWave2D.grid import Grid
from LightWave2D.experiment import Experiment
import LightWave2D.units as units


@pytest.fixture
def grid():
    return Grid(
        resolution=1 * units.micrometer,
        size_x=10 * units.micrometer,
        size_y=5 * units.micrometer,
        n_steps=20
    )


@pytest.fixture
def experiment(grid):
    return Experiment(grid=grid)

