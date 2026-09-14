"""Analytic planar-pulse benchmarks in normalized units (epsilon0=mu0=c=1).

The transverse domain is wide enough that its edges cannot influence the
central detector during the measurement windows. Gaussian excitation starts
four pulse widths after t=0. Tests use the native SI-array interface so the
numerical solver can be checked independently of units and geometry parsing.
"""

import numpy as np
from LightWave2D.binary.interface_simulator import FDTDSimulator
from LightWave2D.source import Pulse


def plane(
    dx=1.0, dielectric=False, absorbing=False, boundary=False, monitor=False, axis=0
):
    nx = int(260 / dx)
    steps = int(360 / dx)
    ny = steps + 5
    dt = 0.5 * dx
    t = np.arange(steps) * dt
    eps = np.ones((nx, ny))
    zero = np.zeros_like(eps)
    sigma = zero.copy()
    if dielectric:
        eps[int(140 / dx) :] = 4
    if absorbing:
        ramp = np.maximum((np.arange(nx) * dx - 210) / 49, 0) ** 3
        sigma[:] = ramp[:, None] * 0.3
    sim = FDTDSimulator()
    indexes = np.array(
        [[int((180 if boundary else 80) / dx), j] for j in range(ny)], dtype=np.int64
    )
    det = np.array(
        [[int(x / dx), ny // 2] for x in ([200] if boundary else [100, 110, 170])],
        dtype=np.int64,
    )
    locations = np.array(
        [[int(x / dx), ny // 2 + j, axis] for x in (110, 170) for j in range(-2, 3)],
        dtype=np.int64,
    )
    if axis == 1:
        nx, ny = ny, nx
        eps, zero, sigma = eps.T.copy(), zero.T.copy(), sigma.T.copy()
        indexes = indexes[:, ::-1].copy()
        det = det[:, ::-1].copy()
        locations[:, :2] = locations[:, :2][:, ::-1]
    sim._cpp_set_config(dt, dx, dx, nx, ny, t)
    sim._cpp_set_geometry_mesh(
        eps, zero, zero, sigma if axis == 0 else zero, sigma if axis == 1 else zero, 1.0
    )
    sim._cpp_set_sources([Pulse(1.0, 6.0, 24.0, indexes)])
    flux_data = np.empty((steps, len(locations), 2))
    if monitor:
        sim._cpp_set_monitors(flux_data, locations)
    data = np.empty((steps, len(det)))
    sim._cpp_run(np.empty((0, nx, ny)), 1, data, det)
    if monitor:
        return t, data, flux_data, locations
    return t, data


def test_vacuum_propagation_speed():
    t, data = plane()
    arrival = [t[np.argmax(data[:, column])] for column in (0, 1)]
    assert abs(10 / (arrival[1] - arrival[0]) - 1) < 0.02


def test_dielectric_interface_fresnel_amplitudes():
    t, reference = plane()
    _, data = plane(dielectric=True)
    incident = reference[t < 80, 1].max()
    reflected = (data - reference)[(t > 95) & (t < 130), 1].min()
    transmitted = data[(t > 130) & (t < 160), 2].max()
    # Normal incidence from n=1 to n=2: r=-1/3, t=2/3.
    assert abs(reflected / incident + 1 / 3) < 0.025
    assert abs(transmitted / incident - 2 / 3) < 0.04
    assert (
        abs((reflected / incident) ** 2 + 2 * (transmitted / incident) ** 2 - 1) < 0.1
    )


def test_mesh_refinement_reduces_pulse_error():
    errors = []
    for dx in (1.0, 0.5):
        t, data = plane(dx)
        window = (t > 95) & (t < 133)
        exact = np.exp(-(((t - 114) / 6) ** 2))
        errors.append(np.sqrt(np.mean((data[window, 2] - exact[window]) ** 2)))
    assert errors[0] < 0.02
    assert errors[1] < 0.5 * errors[0]


def test_absorbing_boundary_reduces_returning_pulse():
    t, bare = plane(boundary=True)
    _, absorbed = plane(boundary=True, absorbing=True)
    window = t > 100
    # This is a regression target for the existing graded conductivity layer,
    # not a claim of perfectly matched absorption: about 25% amplitude remains.
    bare_reflection = np.max(np.abs(bare[window]))
    assert bare_reflection > 0.95
    assert np.max(np.abs(absorbed[window])) < 0.3 * bare_reflection
