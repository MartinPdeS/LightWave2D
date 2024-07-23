import numpy as np
from LightWave2D.grid import Grid


def test_grid_initialization():
    grid = Grid(
        resolution=1e-6,
        size_x=32e-6,
        size_y=16e-6,
        n_steps=3000
    )
    assert grid.n_x == 32
    assert grid.n_y == 16
    assert grid.dx == 1e-6
    assert grid.dy == 1e-6
    assert grid.n_steps == 3000


def test_get_coordinate():
    grid = Grid(
        resolution=1e-6,
        size_x=32e-6,
        size_y=16e-6,
        n_steps=3000
    )
    coord_origin = grid.get_coordinate(0, 0)
    assert coord_origin.x == 0
    assert coord_origin.y == 0
    assert coord_origin.x_index == 0
    assert coord_origin.y_index == 0

    coord_left = grid.get_coordinate('left', 0)
    assert coord_left.x == 0
    assert coord_left.y == 0
    assert coord_left.x_index == 0
    assert coord_left.y_index == 0

    coord_right = grid.get_coordinate('right', 0)
    assert coord_right.x == grid.size_x - grid.dx
    assert coord_right.y == 0
    assert coord_right.x_index == grid.n_x - 1
    assert coord_right.y_index == 0

    coord_center = grid.get_coordinate('center', 0)
    assert coord_center.x == np.mean(grid.x_stamp)
    assert coord_center.y == 0
    # assert coord_center.x_index == int(grid.n_x / 2)
    assert coord_center.y_index == 0

    coord_top = grid.get_coordinate(0, 'top')
    assert coord_top.x == 0
    assert coord_top.y == grid.size_y - grid.dy
    assert coord_top.x_index == 0
    assert coord_top.y_index == grid.n_y - 1

    coord_center_y = grid.get_coordinate(0, 'center')
    assert coord_center_y.x == 0
    assert coord_center_y.y == np.mean(grid.y_stamp)
    assert coord_center_y.x_index == 0
    # assert coord_center_y.y_index == int(grid.n_y / 2)

    coord_bottom = grid.get_coordinate(0, 'bottom')
    assert coord_bottom.x == 0
    assert coord_bottom.y == 0
    assert coord_bottom.x_index == 0
    assert coord_bottom.y_index == 0


def test_get_distance_grid():
    grid = Grid(
        resolution=1e-6,
        size_x=32e-6,
        size_y=16e-6,
        n_steps=3000
    )
    distance_grid = grid.get_distance_grid(0, 0)
    assert isinstance(distance_grid, np.ndarray)
    assert distance_grid.shape == (grid.n_y, grid.n_x)
    assert distance_grid[0, 0] == 0  # Distance from the origin to itself
    # Check the distance at the opposite corner of the grid
    assert np.isclose(distance_grid[-1, -1], np.sqrt((grid.size_x - grid.dx)**2 + (grid.size_y - grid.dy)**2))

# -
