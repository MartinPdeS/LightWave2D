"""Result lifetime and compatibility across repeated simulation runs."""

import numpy as np
import matplotlib.pyplot as plt
import pytest
from TypedUnit import ureg
from LightWave2D.result import SimulationResult


def test_results_survive_repeated_runs(experiment):
    experiment.add_point_pulse(
        position=("center", "center"),
        amplitude=1.0,
        duration=2 * ureg.femtosecond,
    )
    detector = experiment.add_point_detector(position=("center", "center"))
    first = experiment.run(store_every=2)
    assert isinstance(first, SimulationResult)
    assert first is experiment.result
    assert first.Ez_t is experiment.Ez_t
    np.testing.assert_array_equal(first.detector_data[:, 0], detector.data)
    fields = first.Ez_t.copy()
    signals = first.detector_data.copy()
    experiment.sources.clear()
    second = experiment.run(store_fields=False)
    assert second.Ez_t is None
    assert not second.detector_data.any()
    np.testing.assert_array_equal(first.Ez_t, fields)
    np.testing.assert_array_equal(first.detector_data, signals)
    assert not np.shares_memory(first.detector_data, second.detector_data)
    figure = first.plot_frame(0)
    plt.close(figure)
    with pytest.raises(RuntimeError, match="No field history"):
        second.plot_frame(0)


def test_animation_uses_recorded_timestamps(experiment):
    result = experiment.run(store_every=3)
    animation = result.render_propagation(skip_frame=1, show=False)
    artists = animation._func(2)
    assert artists[-1].get_text() == f"time: {result.recorded_time_stamp[2]:.1e}"
    assert result.recorded_time_stamp[2] == experiment.grid.time_stamp[6]
    plt.close(animation._fig)


def test_repeated_run_refreshes_material_coefficients(experiment):
    experiment.add_point_pulse(
        position=("center", "center"),
        amplitude=1.0,
        duration=2 * ureg.femtosecond,
    )
    first = experiment.run()
    repeated = experiment.run()
    np.testing.assert_array_equal(first.Ez_t, repeated.Ez_t)
    experiment.add_circle(
        position=("center", "center"), epsilon_r=4.0, radius=2 * ureg.micrometer
    )
    changed = experiment.run()
    assert not np.allclose(first.Ez_t, changed.Ez_t)
