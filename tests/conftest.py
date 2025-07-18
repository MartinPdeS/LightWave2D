import pytest
from LightWave2D.grid import Grid
from LightWave2D.experiment import Experiment


@pytest.fixture
def grid():
    return Grid(resolution=1e-6, size_x=10e-6, size_y=5e-6, n_steps=20)


@pytest.fixture
def experiment(grid):
    return Experiment(grid=grid)

