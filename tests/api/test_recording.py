"""Independent recording cadences and persistent field history."""

import numpy as np
import pytest
from TypedUnit import ureg
from LightWave2D.result import SimulationResult


def excite(experiment):
    experiment.add_point_pulse(
        position=("center", "center"), amplitude=1.0, duration=2 * ureg.femtosecond
    )
    return experiment.add_point_detector(position=("center", "center"))


def test_independent_sampling_matches_full_history(experiment):
    detector = excite(experiment)
    full = experiment.run()
    sparse = experiment.run(field_every=3, detector_every=2)
    np.testing.assert_array_equal(sparse.Ez_t, full.Ez_t[::3])
    np.testing.assert_array_equal(sparse.detector_data, full.detector_data[::2])
    np.testing.assert_array_equal(
        detector.time_stamp.to("second").magnitude,
        full.detector_time_stamp[::2].to("second").magnitude,
    )
    np.testing.assert_array_equal(
        sparse.recorded_time_stamp.to("second").magnitude,
        full.recorded_time_stamp[::3].to("second").magnitude,
    )
    spectrum = sparse.detector_spectrum()
    expected_dt = (2 * experiment.grid.dt).to("second").magnitude
    assert spectrum.frequency[1] == pytest.approx(
        1 / (len(sparse.detector_data) * expected_dt)
    )
    signal = experiment.run(store_fields=False, field_every=5, detector_every=1)
    np.testing.assert_array_equal(signal.detector_data, full.detector_data)


def test_disk_recording_round_trip(experiment, tmp_path):
    excite(experiment)
    expected = experiment.run(field_every=3)
    path = tmp_path / "fields.npy"
    saved = experiment.run(field_every=3, detector_every=1, field_path=path)
    assert isinstance(saved.Ez_t, np.memmap)
    assert saved.field_path == path
    loaded = SimulationResult.load_fields(path)
    assert isinstance(loaded.Ez_t, np.memmap)
    assert not loaded.Ez_t.flags.writeable
    np.testing.assert_array_equal(loaded.Ez_t, expected.Ez_t)
    np.testing.assert_array_equal(
        loaded.recorded_time_stamp.to("second").magnitude,
        expected.recorded_time_stamp.to("second").magnitude,
    )
    np.testing.assert_array_equal(
        loaded.grid.x_stamp.to("meter").magnitude,
        expected.grid.x_stamp.to("meter").magnitude,
    )
    with pytest.raises(FileExistsError):
        experiment.run(field_path=path)
    np.testing.assert_array_equal(np.load(path), expected.Ez_t)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"field_every": 0},
        {"detector_every": -1},
        {"detector_every": 1.5},
        {"field_every": True},
    ],
)
def test_invalid_intervals(experiment, kwargs):
    with pytest.raises(ValueError):
        experiment.run(**kwargs)


def test_disk_output_requires_fields(experiment, tmp_path):
    path = tmp_path / "fields.npy"
    with pytest.raises(ValueError):
        experiment.run(store_fields=False, field_path=path)
    assert not path.exists()
