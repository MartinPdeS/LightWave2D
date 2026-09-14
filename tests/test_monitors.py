"""Analytic Fourier amplitudes, flux direction, and monitor integration."""

import numpy as np
import pytest
from TypedUnit import ureg
from LightWave2D.monitors import FluxRecord, FluxSpectrum, fourier


def test_fourier_amplitude_and_frequency():
    times = np.arange(128) / 128 * ureg.second
    signal = 3 * np.cos(2 * np.pi * 8 * times.magnitude + 0.3)
    frequency, amplitude = fourier(signal, times, "boxcar")
    assert frequency[np.argmax(abs(amplitude))] == 8
    np.testing.assert_allclose(amplitude[8], 3 * np.exp(0.3j), atol=1e-12)


def test_flux_integration_reference_subtraction_and_normalization():
    times = np.arange(128) / 128 * ureg.second
    wave = np.cos(2 * np.pi * 8 * times.magnitude)
    indexes = np.array([[2, y, 0] for y in range(1, 4)])

    def record(e, h, normal=1):
        data = np.stack(
            [np.tile(e[:, None], (1, 3)), np.tile(h[:, None], (1, 3))], axis=-1
        )
        return FluxRecord(data, times, indexes, 0.5, normal)

    incident = record(wave, wave)
    total = record(0.8 * wave, 1.2 * wave)  # reflected E=-.2, H=+.2
    reference = incident.spectrum(window="boxcar")
    reflected = total.spectrum(window="boxcar", subtract=incident)
    assert reference.power[8] == pytest.approx(0.5)
    assert reflected.normalized(reference)[8] == pytest.approx(-0.04)
    assert np.isnan(reflected.normalized(reference)[1])
    opposite = record(wave, wave, -1).spectrum(window="boxcar")
    assert opposite.power[8] == pytest.approx(-0.5)
    dc = record(np.ones(128), np.ones(128)).spectrum(window="boxcar")
    assert dc.power[0] == pytest.approx(1.0)


def test_reference_validation():
    a = FluxSpectrum(np.array([0.0, 1.0]), np.ones(2))
    b = FluxSpectrum(np.array([0.0, 2.0]), np.ones(2))
    with pytest.raises(ValueError, match="bins"):
        a.normalized(b)
    with pytest.raises(ValueError):
        fourier(np.ones(3), np.array([0, 1, 3]) * ureg.second)


def test_monitor_runs_without_field_history(experiment):
    experiment.add_point_pulse(
        position=("center", "center"), amplitude=1.0, duration=2 * ureg.femtosecond
    )
    experiment.add_flux_monitor(position_0=("60%", "25%"), position_1=("60%", "75%"))
    experiment.add_flux_monitor(
        position_0=("25%", "50%"), position_1=("75%", "50%"), normal=-1
    )
    result = experiment.run(store_fields=False, detector_every=2)
    assert result.Ez_t is None
    assert len(result.flux) == 2
    assert result.flux[0].data.shape[0] == 10
    assert np.any(result.flux[0].data)
    np.testing.assert_array_equal(
        result.flux[0].time_stamp.to("second").magnitude,
        (experiment.grid.time_stamp[::2] - experiment.grid.dt / 2)
        .to("second")
        .magnitude,
    )
    assert np.isfinite(result.flux[0].spectrum().power).all()
    old = result.flux[0].data.copy()
    full = experiment.run()
    np.testing.assert_array_equal(old, full.flux[0].data[::2])
    np.testing.assert_array_equal(old, result.flux[0].data)


@pytest.mark.parametrize(
    "start,end",
    [
        (("20%", "20%"), ("80%", "80%")),
        (("0%", "20%"), ("0%", "80%")),
        (("50%", "50%"), ("50%", "50%")),
    ],
)
def test_invalid_monitor_geometry(experiment, start, end):
    with pytest.raises(ValueError):
        experiment.add_flux_monitor(position_0=start, position_1=end)


@pytest.mark.parametrize("axis", [0, 1])
def test_native_flux_fresnel_spectra(axis):
    from tests.test_physics_accuracy import plane

    t, _, vacuum, locations = plane(monitor=True, axis=axis)
    _, _, dielectric, _ = plane(monitor=True, dielectric=True, axis=axis)
    times = (t - 0.25) * ureg.second

    def record(data, start):
        return FluxRecord(
            data[:, start : start + 5], times, locations[start : start + 5], 1.0, 1
        )

    incident = record(vacuum, 0)
    incident_power = incident.spectrum(window="boxcar")
    reflected = record(dielectric, 0).spectrum(window="boxcar", subtract=incident)
    transmitted = record(dielectric, 5).spectrum(window="boxcar")
    band = (incident_power.frequency > 0) & (incident_power.frequency < 0.025)
    reflection = -reflected.normalized(incident_power)[band]
    transmission = transmitted.normalized(incident_power)[band]
    np.testing.assert_allclose(reflection, 1 / 9, atol=0.025)
    np.testing.assert_allclose(transmission, 8 / 9, atol=0.025)
    np.testing.assert_allclose(reflection + transmission, 1.0, atol=0.025)
