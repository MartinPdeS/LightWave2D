from LightWave2D.source import VerticalLineSource
from LightWave2D.grid import Grid


def test_source():
    grid = Grid(
        n_x=400,
        n_y=200,
        size_x=8e-6,
        size_y=4e-6,
        n_steps=30
    )

    source = VerticalLineSource(
        grid=grid,
        wavelength=15500e-9,
        x_position=1e-6,
        amplitude=0.1,
        y_positions=(7e-6, 9e-6)
    )

    source.plot()


# -
