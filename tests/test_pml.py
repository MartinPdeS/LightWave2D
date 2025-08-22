import numpy as np
import pytest
from TypedUnit import ureg

from LightWave2D.grid import Grid
from LightWave2D.pml import PML



def create_simple_grid():
    return Grid(
        resolution=1 * ureg.micrometer,
        size_x=10 * ureg.micrometer,
        size_y=5 * ureg.micrometer,
        n_steps=10,
    )


def test_pml_conductivity_profile():
    grid = create_simple_grid()
    boundary_layer = PML(grid=grid, width="20%", sigma_max=1 * (ureg.siemens / ureg.meter), order=1)

    assert boundary_layer.sigma_x.shape == (grid.n_x, grid.n_y)
    assert boundary_layer.sigma_y.shape == (grid.n_x, grid.n_y)

    interior_slice_x = boundary_layer.sigma_x[
        boundary_layer.width_start.x_index + 1 : boundary_layer.width_stop.x_index - 1,
        boundary_layer.width_start.y_index + 1 : boundary_layer.width_stop.y_index - 1,
    ]
    interior_slice_y = boundary_layer.sigma_y[
        boundary_layer.width_start.x_index + 1 : boundary_layer.width_stop.x_index - 1,
        boundary_layer.width_start.y_index + 1 : boundary_layer.width_stop.y_index - 1,
    ]
    assert np.allclose(interior_slice_x, 0)
    assert np.allclose(interior_slice_y, 0)
    assert np.any(boundary_layer.sigma_x > 0)
    assert np.any(boundary_layer.sigma_y > 0)


@pytest.mark.parametrize("method", ["parse_x_position", "parse_y_position"])
def test_invalid_position_strings(method):
    grid = create_simple_grid()
    with pytest.raises(AssertionError):
        getattr(grid, method)("invalid")



if __name__ == "__main__":
    pytest.main(["-W error", "-s", __file__])

