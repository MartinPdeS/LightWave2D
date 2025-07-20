import pytest
from LightWave2D.grid import Grid
from LightWave2D.experiment import Experiment
import LightWave2D.units as units


# Test the grid initialization
def test_grid_initialization(grid):
    assert grid.resolution == 1 * units.micrometer
    assert grid.size_x == 10 * units.micrometer
    assert grid.size_y == 5 * units.micrometer
    assert grid.n_steps == 20


# Test the experiment initialization
def test_experiment_initialization(experiment, grid):
    assert experiment.grid == grid


# Test adding scatterers
@pytest.mark.parametrize("method, params", [
    (
        'add_square',
        {
            'position': ('25%', '20%'),
            'epsilon_r': 2,
            'side_length': 3 * units.micrometer
        }
    ),
    (
        'add_ellipse',
        {
            'position': ('25%', '70%'),
            'epsilon_r': 2,
            'width': 5 * units.micrometer,
            'height': 10 * units.micrometer,
            'rotation': 10
        }
    )
])
def test_add_scatterers(experiment, method, params):
    scatterer = getattr(experiment, method)(**params)
    assert scatterer in experiment.components  # Assuming components is a list of added elements


# Test adding sources
@pytest.mark.parametrize("method, params", [
    (
        'add_point_source',
        {
            'wavelength': 1550 * units.nanometer,
            'position': ('30%', '70%'),
            'amplitude': 10
        }
    ),
    (
        'add_line_source',
        {
            'wavelength': 1550 * units.nanometer,
            'position_0': ('10%', '100%'),
            'position_1': ('10%', '0%'),
            'amplitude': 10
        }
    )
])
def test_add_sources(experiment, method, params):
    source = getattr(experiment, method)(**params)
    assert source in experiment.sources  # Assuming sources is a list of added elements


# Test adding a PML
def test_add_pml(experiment):
    pml = experiment.add_pml(order=1, width='10%', sigma_max=5000 * (units.siemens / units.meter))
    assert pml is not None  # Assuming pmls is a list of added elements


# Test adding a detector
def test_add_detector(experiment):
    detector = experiment.add_point_detector(position=(5 * units.micrometer, 5 * units.micrometer))
    assert detector in experiment.detectors  # Assuming detectors is a list of added elements


@pytest.mark.skip("Heavy computation not required for unit testing")
def test_experiment_run_and_render(experiment):
    experiment.run_fdtd()
    animation = experiment.render_propagation(skip_frame=5)
    animation.save('./tests.gif', writer='Pillow', fps=10)


if __name__ == "__main__":
    pytest.main(["-W error", "-s", __file__])
