import numpy as np
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


if __name__ == "__main__":
    pytest.main(["-W error", "-s", __file__])

