import pytest
from unittest.mock import patch
from LightWave2D.grid import Grid
from LightWave2D.experiment import Experiment


# Test the grid initialization
def test_grid_initialization():
    grid = Grid(resolution=0.1e-6, size_x=30e-6, size_y=30e-6, n_steps=500)
    assert grid.resolution == 0.1e-6
    assert grid.size_x == 30e-6
    assert grid.size_y == 30e-6
    assert grid.n_steps == 500


# Test the experiment initialization
def test_experiment_initialization():
    grid = Grid(resolution=0.1e-6, size_x=30e-6, size_y=30e-6, n_steps=500)
    experiment = Experiment(grid=grid)
    assert experiment.grid == grid


# Test adding scatterers
@pytest.mark.parametrize("method, params", [
    ('add_square', {'position': ('25%', '20%'), 'epsilon_r': 2, 'side_length': 3e-6}),
    ('add_ellipse', {'position': ('25%', '70%'), 'epsilon_r': 2, 'width': 5e-6, 'height': 10e-6, 'rotation': 10})
])
def test_add_scatterers(method, params):
    grid = Grid(resolution=0.1e-6, size_x=30e-6, size_y=30e-6, n_steps=500)
    experiment = Experiment(grid=grid)
    scatterer = getattr(experiment, method)(**params)
    assert scatterer in experiment.components  # Assuming components is a list of added elements


# Test adding sources
@pytest.mark.parametrize("method, params", [
    ('add_point_source', {'wavelength': 1550e-9, 'position': ('30%', '70%'), 'amplitude': 10}),
    ('add_line_source', {'wavelength': 1550e-9, 'position_0': ('10%', '100%'), 'position_1': ('10%', '0%'), 'amplitude': 10})
])
def test_add_sources(method, params):
    grid = Grid(resolution=0.1e-6, size_x=30e-6, size_y=30e-6, n_steps=500)
    experiment = Experiment(grid=grid)
    source = getattr(experiment, method)(**params)
    assert source in experiment.sources  # Assuming sources is a list of added elements


# Test adding a PML
def test_add_pml():
    grid = Grid(resolution=0.1e-6, size_x=30e-6, size_y=30e-6, n_steps=500)
    experiment = Experiment(grid=grid)
    pml = experiment.add_pml(order=1, width='10%', sigma_max=5000)
    assert pml is not None  # Assuming pmls is a list of added elements


# Test adding a detector
def test_add_detector():
    grid = Grid(resolution=0.1e-6, size_x=30e-6, size_y=30e-6, n_steps=500)
    experiment = Experiment(grid=grid)
    detector = experiment.add_point_detector(position=(25e-6, 'center'))
    assert detector in experiment.detectors  # Assuming detectors is a list of added elements


# Mock the plot and animation functions to avoid graphical output during tests
@patch('LightWave2D.experiment.Experiment.plot')
@patch('LightWave2D.experiment.Experiment.render_propagation')
def test_experiment_run_and_render(mock_render_propagation, mock_plot):
    grid = Grid(resolution=0.1e-6, size_x=30e-6, size_y=30e-6, n_steps=500)
    experiment = Experiment(grid=grid)
    experiment.run_fdtd()
    experiment.plot()
    mock_plot.assert_called_once()
    animation = experiment.render_propagation(skip_frame=5)
    mock_render_propagation.assert_called_once_with(skip_frame=5)
    animation.save('./tests.gif', writer='Pillow', fps=10)

# -
