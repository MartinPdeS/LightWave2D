import numpy as np
import pytest
from LightWave2D.physics import Physics


def test_get_gradient(experiment):
    # simple field increasing linearly along x and y
    field_x = np.tile(np.arange(experiment.grid.n_x)[:, None], (1, experiment.grid.n_y))
    grad_x = experiment.get_gradient(field_x, axis="x")

    field_y = np.tile(np.arange(experiment.grid.n_y)[None, :], (experiment.grid.n_x, 1))
    grad_y = experiment.get_gradient(field_y, axis="y")

    assert grad_x.shape == (experiment.grid.n_x - 1, experiment.grid.n_y)
    assert np.allclose(grad_x, 1 / experiment.grid.dx)
    assert grad_y.shape == (experiment.grid.n_x, experiment.grid.n_y - 1)
    assert np.allclose(grad_y, 1 / experiment.grid.dy)


def test_get_epsilon_sigma_without_components(experiment):
    sigma_x, sigma_y = experiment.get_sigma()
    epsilon = experiment.get_epsilon()

    assert not sigma_x.any()
    assert not sigma_y.any()
    expected = np.ones(experiment.grid.shape) * Physics.epsilon_0
    assert np.allclose(epsilon, expected)


def test_run_produces_a_finite_field_and_detector_signal():
    from TypedUnit import ureg
    from LightWave2D.experiment import Experiment
    from LightWave2D.grid import Grid

    grid = Grid(
        resolution=1 * ureg.micrometer,
        size_x=12 * ureg.micrometer,
        size_y=8 * ureg.micrometer,
        n_steps=6,
    )
    simulation = Experiment(grid=grid)
    simulation.add_point_source(
        wavelength=1.55 * ureg.micrometer,
        position=("center", "center"),
        amplitude=1.0,
    )
    detector = simulation.add_point_detector(position=("center", "center"))

    simulation.run()

    assert simulation.Ez_t.shape == (grid.n_steps, *grid.shape)
    assert np.isfinite(simulation.Ez_t).all()
    assert np.max(np.abs(simulation.Ez_t)) > 0
    assert np.array_equal(
        detector.data, simulation.Ez_t[:, detector.p0.x_index, detector.p0.y_index]
    )


def test_run_accepts_components_with_a_pml():
    from TypedUnit import ureg
    from LightWave2D.experiment import Experiment
    from LightWave2D.grid import Grid

    grid = Grid(
        resolution=1 * ureg.micrometer,
        size_x=12 * ureg.micrometer,
        size_y=8 * ureg.micrometer,
        n_steps=4,
    )
    simulation = Experiment(grid=grid)
    simulation.add_pml(width="20%")
    simulation.add_circle(
        position=("center", "center"), epsilon_r=2.0, radius=1 * ureg.micrometer
    )
    simulation.add_point_pulse(
        position=("center", "center"), amplitude=1.0, duration=1 * ureg.femtosecond
    )

    simulation.run(store_fields=False)


def test_plot_accepts_native_pml_component_and_source():
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure
    from TypedUnit import ureg
    from LightWave2D.experiment import Experiment
    from LightWave2D.grid import Grid

    grid = Grid(
        resolution=0.2 * ureg.micrometer,
        size_x=52 * ureg.micrometer,
        size_y=40 * ureg.micrometer,
        n_steps=4,
    )
    simulation = Experiment(grid=grid)
    simulation.add_pml(width="20%")
    simulation.add_circle(
        position=("center", "center"), epsilon_r=2.0, radius=4 * ureg.micrometer
    )
    simulation.add_line_pulse(
        position_0=("30%", "60%"),
        position_1=("30%", "40%"),
        amplitude=1.0,
        duration=1 * ureg.femtosecond,
    )

    figure = Figure()
    FigureCanvasAgg(figure)
    axis = figure.subplots()
    simulation.plot(ax=axis, show=False)


def test_render_saves_a_gif_with_native_components(tmp_path):
    from TypedUnit import ureg
    from LightWave2D.experiment import Experiment
    from LightWave2D.grid import Grid

    grid = Grid(
        resolution=1 * ureg.micrometer,
        size_x=8 * ureg.micrometer,
        size_y=6 * ureg.micrometer,
        n_steps=4,
    )
    simulation = Experiment(grid=grid)
    simulation.add_circle(
        position=("center", "center"), epsilon_r=2.0, radius=1 * ureg.micrometer
    )
    simulation.add_point_pulse(
        position=("center", "center"), amplitude=1.0, duration=1 * ureg.femtosecond
    )
    simulation.run()

    output = tmp_path / "propagation.gif"
    simulation.render_propagation(skip_frame=1, fps=4, save_as=output, show=False)
    assert output.exists()
    assert output.stat().st_size > 0


def test_run_can_downsample_field_and_detector_storage():
    from TypedUnit import ureg
    from LightWave2D.experiment import Experiment
    from LightWave2D.grid import Grid

    grid = Grid(
        resolution=1 * ureg.micrometer,
        size_x=12 * ureg.micrometer,
        size_y=8 * ureg.micrometer,
        n_steps=6,
    )
    simulation = Experiment(grid=grid)
    simulation.add_point_source(
        wavelength=1.55 * ureg.micrometer, position=("center", "center"), amplitude=1.0
    )
    detector = simulation.add_point_detector(position=("center", "center"))

    simulation.run(store_every=2)

    assert simulation.Ez_t.shape == (3, *grid.shape)
    assert np.all(simulation.recorded_time_stamp == grid.time_stamp[::2])
    assert np.array_equal(
        detector.data, simulation.Ez_t[:, detector.p0.x_index, detector.p0.y_index]
    )


def test_run_supports_detector_only_mode():
    from TypedUnit import ureg
    from LightWave2D.experiment import Experiment
    from LightWave2D.grid import Grid

    grid = Grid(
        resolution=1 * ureg.micrometer,
        size_x=12 * ureg.micrometer,
        size_y=8 * ureg.micrometer,
        n_steps=6,
    )
    simulation = Experiment(grid=grid)
    simulation.add_point_source(
        wavelength=1.55 * ureg.micrometer, position=("center", "center"), amplitude=1.0
    )
    detector = simulation.add_point_detector(position=("center", "center"))

    simulation.run(store_fields=False, store_every=2)

    assert simulation.Ez_t is None
    assert detector.data.shape == (3,)
    assert np.max(np.abs(detector.data)) > 0
    with pytest.raises(RuntimeError, match="No field history"):
        simulation.render_propagation(show=False)


@pytest.mark.parametrize("store_every", [0, -1, 1.5])
def test_run_rejects_invalid_recording_interval(experiment, store_every):
    with pytest.raises(ValueError, match="store_every"):
        experiment.run(store_every=store_every)


if __name__ == "__main__":
    pytest.main(["-W error", "-s", __file__])
