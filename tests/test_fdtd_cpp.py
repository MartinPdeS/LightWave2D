import numpy as np
from LightWave2D.binary import fdtd_simulation, SourceInterface


def test_fdtd_no_sources():
    n_steps = 1
    nx, ny = 3, 3
    ez = np.zeros((n_steps, nx, ny), dtype=float)
    zeros = np.zeros((nx, ny), dtype=float)
    ones = np.ones((nx, ny), dtype=float)
    time = np.arange(n_steps, dtype=float)

    fdtd_simulation.run_fdtd(
        Ez=ez,
        time_stamp=time,
        sigma_x=zeros,
        sigma_y=zeros,
        epsilon=ones,
        gamma=zeros,
        n2=zeros,
        dt=1.0,
        mu_0=1.0,
        n_steps=n_steps,
        dx=1.0,
        dy=1.0,
        nx=nx,
        ny=ny,
        sources=[],
    )

    assert np.all(ez == 0.0)


def test_fdtd_with_source():
    n_steps = 1
    nx, ny = 3, 3
    ez = np.zeros((n_steps, nx, ny), dtype=float)
    zeros = np.zeros((nx, ny), dtype=float)
    ones = np.ones((nx, ny), dtype=float)
    time = np.arange(n_steps, dtype=float)

    omega = np.array([1.0])
    amplitude = np.array([2.0])
    delay = np.array([0.0])
    indexes = np.array([[1, 1]], dtype=np.int64)
    source = SourceInterface.MultiWavelength(omega, amplitude, delay, indexes)

    fdtd_simulation.run_fdtd(
        Ez=ez,
        time_stamp=time,
        sigma_x=zeros,
        sigma_y=zeros,
        epsilon=ones,
        gamma=zeros,
        n2=zeros,
        dt=1.0,
        mu_0=1.0,
        n_steps=n_steps,
        dx=1.0,
        dy=1.0,
        nx=nx,
        ny=ny,
        sources=[source],
    )

    expected = amplitude[0] * np.cos(omega[0] * time[0] + delay[0])
    assert ez[0, 1, 1] == expected
