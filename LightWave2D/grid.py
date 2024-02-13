import numpy
from dataclasses import dataclass
from LightWave2D.physics import Physics


class NameSpace():
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


@dataclass()
class Grid():
    n_x: int
    """ Number of cells in the x-direction """
    n_y: int
    """  Number of cells in the y-direction """
    size_x: float
    """ Size of the grid in x-direction in meters """
    size_y: float
    """ Size of the grid in y-direction in meters """
    n_steps: int = 200
    """ Number of time steps for the simulation """

    def __post_init__(self):
        self.shape = self.n_x, self.n_y

        self.dx = self.size_x / (self.n_x)

        self.dy = self.size_y / (self.n_y)

        self.dt = 1 / (Physics.c * numpy.sqrt(1 / self.dx**2 + 1 / self.dy**2))  # Time step size using Courant condition

        self.time_stamp = numpy.arange(self.n_steps) * self.dt

        self.x_stamp = numpy.arange(self.n_x) * self.dx

        self.y_stamp = numpy.arange(self.n_y) * self.dy

    def get_distance_grid(self, x0: float = 0, y0: float = 0) -> numpy.ndarray:
        x_mesh, y_mesh = numpy.meshgrid(self.y_stamp, self.x_stamp)

        x_mesh -= x0

        y_mesh -= y0

        distance_mesh = numpy.sqrt(numpy.square(x_mesh) + numpy.square(y_mesh))

        return distance_mesh

    def get_coordinate(self, x: float | str = None, y: float | str = None) -> NameSpace:
        coordinate = NameSpace()
        if isinstance(x, str):
            x = self.string_to_position_x(x)

        if isinstance(y, str):
            y = self.string_to_position_y(y)

        if x is not None:
            x = numpy.clip(x, self.x_stamp[0], self.x_stamp[-1])
            x_index = int(x / self.dx)

            coordinate.x = x
            coordinate.x_index = x_index

        if y is not None:
            y = numpy.clip(y, self.y_stamp[0], self.y_stamp[-1])
            y_index = int(y / self.dx)

            coordinate.y = y
            coordinate.y_index = y_index

        return coordinate

    def string_to_position_y(self, position_string: str) -> int:
        assert position_string in ['bottom', 'center', 'top'], f"Invalid position: {position_string} for y positionning. Valid input are ['bottom', 'center', 'top']"
        match position_string.lower():
            case 'bottom':
                return self.y_stamp[0]
            case 'center':
                return self.y_stamp[self.n_y // 2]
            case 'top':
                return self.y_stamp[-1]

    def string_to_position_x(self, position_string: str) -> int:
        assert position_string in ['left', 'center', 'right'], f"Invalid position: {position_string} for y positionning. Valid input are ['left', 'center', 'right']"
        match position_string.lower():
            case 'left':
                return self.x_stamp[0]
            case 'center':
                return self.x_stamp[self.n_x // 2]
            case 'right':
                return self.x_stamp[-1]


# -
