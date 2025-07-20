import pytest
import numpy as np
from LightWave2D.grid import Grid
import LightWave2D.units as units


@pytest.fixture
def default_grid():
    """Backward compatibility fixture kept for tests using it directly."""
    return Grid(
        resolution=1 * units.micrometer,
        size_x=32 * units.micrometer,
        size_y=16 * units.micrometer,
        n_steps=3000
    )


# List of dictionaries for grid initialization parameters
grid_parameters = [
    dict(
        resolution=1 * units.micrometer,
        size_x=32 * units.micrometer,
        size_y=16 * units.micrometer,
        n_steps=3000,
        expected_n_x=32,
        expected_n_y=16
    ),
    dict(
        resolution=0.5 * units.micrometer,
        size_x=64 * units.micrometer,
        size_y=32 * units.micrometer,
        n_steps=1000,
        expected_n_x=128,
        expected_n_y=64
    ),
    dict(
        resolution=2 * units.micrometer,
        size_x=64 * units.micrometer,
        size_y=32 * units.micrometer,
        n_steps=5000,
        expected_n_x=32,
        expected_n_y=16
    )
]


@pytest.mark.parametrize("params", grid_parameters)
def test_grid_initialization(params):
    grid = Grid(
        resolution=params["resolution"],
        size_x=params["size_x"],
        size_y=params["size_y"],
        n_steps=params["n_steps"]
    )
    assert grid.n_x == params["expected_n_x"], f"Expected n_x to be {params['expected_n_x']}, got {grid.n_x}"
    assert grid.n_y == params["expected_n_y"], f"Expected n_y to be {params['expected_n_y']}, got {grid.n_y}"
    expected_res = params["resolution"]
    assert grid.dx == expected_res, f"Expected dx to be {expected_res}, got {grid.dx}"
    assert grid.dy == expected_res, f"Expected dy to be {expected_res}, got {grid.dy}"
    assert grid.n_steps == params["n_steps"], f"Expected n_steps to be {params['n_steps']}, got {grid.n_steps}"


def test_get_coordinate(default_grid):
    grid = default_grid

    coordinates = [
        {"name": "origin", "x": 0, "y": 0, "expected_x": 0, "expected_y": 0},
        {"name": "left", "x": "left", "y": 0, "expected_x": 0, "expected_y": 0},
        {"name": "right", "x": "right", "y": 0, "expected_x": grid.size_x, "expected_y": 0},
        {"name": "center_x", "x": "center", "y": 0, "expected_x": np.mean(grid.x_stamp), "expected_y": 0},
        {"name": "top", "x": 0, "y": "top", "expected_x": 0, "expected_y": grid.size_y},
        {"name": "center_y", "x": 0, "y": "center", "expected_x": 0, "expected_y": np.mean(grid.y_stamp)},
        {"name": "bottom", "x": 0, "y": "bottom", "expected_x": 0, "expected_y": 0}
    ]

    for coord_info in coordinates:
        coord = grid.get_coordinate(coord_info["x"], coord_info["y"])
        assert coord.x == coord_info["expected_x"], f"[{coord_info['name']}] Expected x to be {coord_info['expected_x']}, got {coord.x}"
        assert coord.y == coord_info["expected_y"], f"[{coord_info['name']}] Expected y to be {coord_info['expected_y']}, got {coord.y}"
        assert isinstance(coord.x_index, int), f"[{coord_info['name']}] x_index should be an integer"
        assert isinstance(coord.y_index, int), f"[{coord_info['name']}] y_index should be an integer"


def test_get_distance_grid(default_grid):
    grid = default_grid
    distance_grid = grid.get_distance_grid(0, 0)

    assert distance_grid.shape == (grid.n_y, grid.n_x), f"Expected shape {(grid.n_y, grid.n_x)}, got {distance_grid.shape}"
    assert distance_grid[0, 0] == 0, "Distance from the origin to itself should be 0"

    # Check the distance at the opposite corner of the grid
    expected_distance = np.sqrt((grid.size_x - grid.dx)**2 + (grid.size_y - grid.dy)**2)
    assert np.isclose(distance_grid[-1, -1], expected_distance, atol=2 * units.micrometer), (
        f"Expected distance at the opposite corner to be approximately {expected_distance}, got {distance_grid[-1, -1]}"
    )


def test_parse_percentage_positions(default_grid):
    grid = default_grid

    x = grid.parse_x_position("50%")
    y = grid.parse_y_position("25%")

    assert x == (0.5 * (grid.x_stamp[-1] - grid.x_stamp[0]))
    assert y == (0.25 * (grid.y_stamp[-1] - grid.y_stamp[0]))


@pytest.mark.parametrize("key,val", [
    ("left", 0),
    ("center", lambda g: (np.mean(g.x_stamp))),
    ("right", lambda g: (g.x_stamp[-1]))
])
def test_parse_x_strings(default_grid, key, val):
    grid = default_grid
    expected = val(grid) if callable(val) else val
    assert grid.parse_x_position(key) == expected


@pytest.mark.parametrize("key,val", [
    ("bottom", 0),
    ("center", lambda g: (np.mean(g.y_stamp))),
    ("top", lambda g: (g.y_stamp[-1]))
])
def test_parse_y_strings(default_grid, key, val):
    grid = default_grid
    expected = val(grid) if callable(val) else val
    assert grid.parse_y_position(key) == expected


@pytest.mark.parametrize(
    "method,value",
    [("parse_x_position", "bad"), ("parse_y_position", "bad")],
)
def test_invalid_parse_strings(default_grid, method, value):
    with pytest.raises(AssertionError):
        getattr(default_grid, method)(value)


def test_grid_initialization_with_units():
    grid = Grid(
        resolution=1 * units.micrometer,
        size_x=32 * units.micrometer,
        size_y=16 * units.micrometer,
        n_steps=100
    )

    assert grid.dx == 1 * units.micrometer
    assert grid.size_x == 32 * units.micrometer
    assert grid.size_y == 16 * units.micrometer




if __name__ == "__main__":
    pytest.main(["-W error", "-s", __file__])
