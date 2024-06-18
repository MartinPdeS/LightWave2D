import numpy as np
from dataclasses import dataclass
from LightWave2D.physics import Physics


class NameSpace:
    """
    A class to dynamically create attributes from keyword arguments.
    """

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


@dataclass
class Grid:
    """
    Represents a 2D simulation grid with specified dimensions and time steps.

    Attributes:
        n_x (int): Number of cells in the x-direction.
        n_y (int): Number of cells in the y-direction.
        size_x (float): Size of the grid in the x-direction in meters.
        size_y (float): Size of the grid in the y-direction in meters.
        n_steps (int): Number of time steps for the simulation (default is 200).
    """
    n_x: int
    n_y: int
    size_x: float
    size_y: float
    n_steps: int = 200

    def __post_init__(self):
        self.shape = (self.n_x, self.n_y)
        self.dx = self.size_x / self.n_x
        self.dy = self.size_y / self.n_y
        self.dt = 1 / (Physics.c * np.sqrt(1 / self.dx**2 + 1 / self.dy**2))  # Time step size using Courant condition

        self.time_stamp = np.arange(self.n_steps) * self.dt
        self.x_stamp = np.arange(self.n_x) * self.dx
        self.y_stamp = np.arange(self.n_y) * self.dy

    def get_distance_grid(self, x0: float = 0, y0: float = 0) -> np.ndarray:
        """
        Compute the distance grid from a given point (x0, y0).

        Args:
            x0 (float): x-coordinate of the reference point (default is 0).
            y0 (float): y-coordinate of the reference point (default is 0).

        Returns:
            np.ndarray: A 2D array of distances from the reference point.
        """
        x_mesh, y_mesh = np.meshgrid(self.x_stamp, self.y_stamp)
        distance_mesh = np.sqrt((x_mesh - x0)**2 + (y_mesh - y0)**2)
        return distance_mesh

    def get_coordinate(self, x: float | str = None, y: float | str = None) -> NameSpace:
        """
        Get the coordinate and index for a given position in the grid.

        Args:
            x (float | str): x-coordinate or position string ('left', 'center', 'right').
            y (float | str): y-coordinate or position string ('bottom', 'center', 'top').

        Returns:
            NameSpace: An object containing the coordinates and indices.
        """
        coordinate = NameSpace()

        if isinstance(x, str):
            x = self.string_to_position_x(x)
        if isinstance(y, str):
            y = self.string_to_position_y(y)

        if x is not None:
            x = np.clip(x, self.x_stamp[0], self.x_stamp[-1])
            coordinate.x = x
            coordinate.x_index = int(x / self.dx)

        if y is not None:
            y = np.clip(y, self.y_stamp[0], self.y_stamp[-1])
            coordinate.y = y
            coordinate.y_index = int(y / self.dy)

        return coordinate

    def string_to_position_y(self, position_string: str) -> float:
        """
        Convert a position string to a y-coordinate.

        Args:
            position_string (str): Position string ('bottom', 'center', 'top').

        Returns:
            float: Corresponding y-coordinate.
        """
        positions = {'bottom': self.y_stamp[0], 'center': self.y_stamp[self.n_y // 2], 'top': self.y_stamp[-1]}
        assert position_string.lower() in positions, f"Invalid position: {position_string}. Valid inputs are ['bottom', 'center', 'top']."
        return positions[position_string.lower()]

    def string_to_position_x(self, position_string: str) -> float:
        """
        Convert a position string to an x-coordinate.

        Args:
            position_string (str): Position string ('left', 'center', 'right').

        Returns:
            float: Corresponding x-coordinate.
        """
        positions = {'left': self.x_stamp[0], 'center': self.x_stamp[self.n_x // 2], 'right': self.x_stamp[-1]}
        assert position_string.lower() in positions, f"Invalid position: {position_string}. Valid inputs are ['left', 'center', 'right']."
        return positions[position_string.lower()]

# -
