
from LightWave2D.grid import Grid


def test_grid():
    grid = Grid(
        resolution=1e-6,
        size_x=32e-6,
        size_y=16e-6,
        n_steps=3000
    )

    _ = grid.get_coordinate(0, 0)

    _ = grid.get_coordinate('left', 0)

    _ = grid.get_coordinate('right', 0)

    _ = grid.get_coordinate('center', 0)

    _ = grid.get_coordinate(0, 'top')

    _ = grid.get_coordinate(0, 'center')

    _ = grid.get_coordinate(0, 'bottom')

    _ = grid.get_distance_grid()


# -
