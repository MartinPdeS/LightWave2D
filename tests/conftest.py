import pytest
from TypedUnit import ureg

from LightWave2D.grid import Grid
from LightWave2D.experiment import Experiment


@pytest.fixture
def grid():
    return Grid(
        resolution=1 * ureg.micrometer,
        size_x=10 * ureg.micrometer,
        size_y=5 * ureg.micrometer,
        n_steps=20
    )


@pytest.fixture
def experiment(grid):
    return Experiment(grid=grid)

