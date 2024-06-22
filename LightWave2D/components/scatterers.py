#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Tuple, Union, NoReturn
from pydantic.dataclasses import dataclass
import numpy
from LightWave2D.grid import Grid
from MPSPlots.render2D import Axis
from LightWave2D.components.base_class import BaseComponent


config_dict = dict(
    kw_only=True,
    extra='forbid',
    slots=True,
    arbitrary_types_allowed=True
)


@dataclass(config=config_dict)
class Waveguide(BaseComponent):
    """
    Represents a waveguide in a simulation grid.

    Attributes:
        grid (Grid): The grid of the simulation mesh.
        width (int | str): Width of the waveguide in grid cells or 'full' for full width.
        height (int | str): Height of the waveguide in grid cells or 'full' for full height.
        position (tuple): Starting position of the waveguide.
        epsilon_r (float): Relative permittivity inside the waveguide.
    """
    grid: Grid
    width: Union[int | str]
    height: Union[int | str]
    position: Tuple[float | str, float | str]
    epsilon_r: float

    def build_mesh(self) -> NoReturn:
        """
        Build the permittivity mesh for the waveguide.
        """
        width_index, height_index = self._interpret_width_height()
        x_index, y_index = self._interpret_position_to_index()

        x_start, x_end = x_index, x_index + width_index
        y_start, y_end = y_index, y_index + height_index

        self.epsilon_r_mesh[x_start:x_end, y_start:y_end] = self.epsilon_r

    def _interpret_width_height(self) -> Tuple[float, float]:
        """
        Interpret and return the width and height of the waveguide in grid indices.

        Returns:
            tuple: The indices of the width and height.
        """
        if isinstance(self.width, str) and self.width.lower() == 'full':
            width_index = self.grid.n_x
        else:
            width_index = self.grid.position_to_index(self.width, axis='x')

        if isinstance(self.height, str) and self.height.lower() == 'full':
            height_index = self.grid.n_y
        else:
            height_index = self.grid.position_to_index(self.height, axis='y')

        return int(width_index), int(height_index)

    def _interpret_position_to_index(self) -> Tuple[int, int]:
        """
        Interpret and return the indices for the positions x and y of the waveguide.

        Returns:
            tuple: The indices of the x and y positions.
        """
        x, y = self.position
        x_index = self.grid.string_to_position_x(x) if isinstance(x, str) else self.grid.position_to_index(x, axis='x')
        y_index = self.grid.string_to_position_y(y) if isinstance(y, str) else self.grid.position_to_index(y, axis='y')
        return x_index, y_index


@dataclass(config=config_dict)
class Square(BaseComponent):
    """
    Represents a square scatterer in a simulation grid.

    Attributes:
        grid (Grid): The grid of the simulation mesh.
        position (Tuple[float | str, float | str]): Starting position of the scatterer (center of the square).
        epsilon_r (float): Relative permittivity inside the scatterer.
        side_length (float): Side length of the square scatterer.
    """
    grid: Grid
    position: Tuple[float | str, float | str]
    epsilon_r: float
    side_length: float

    def build_mesh(self) -> NoReturn:
        """
        Build the permittivity mesh for the square scatterer.
        """
        x0, y0 = self.position
        self.coordinate = self.grid.get_coordinate(x=x0, y=y0)

        half_side = self.side_length / 2
        self.x_start = int((self.coordinate.x - half_side) / self.grid.dx)
        self.x_end = int((self.coordinate.x + half_side) / self.grid.dx)
        self.y_start = int((self.coordinate.y - half_side) / self.grid.dy)
        self.y_end = int((self.coordinate.y + half_side) / self.grid.dy)

        self.epsilon_r_mesh[self.x_start:self.x_end, self.y_start:self.y_end] = self.epsilon_r

        # Create a boolean index array for the square region
        self.idx = (self.grid.x_stamp >= self.x_start * self.grid.dx) & \
                   (self.grid.x_stamp < self.x_end * self.grid.dx) & \
                   (self.grid.y_stamp[:, None] >= self.y_start * self.grid.dy) & \
                   (self.grid.y_stamp[:, None] < self.y_end * self.grid.dy)

        self.idx = self.idx.T

    def add_to_ax(self, ax: Axis) -> NoReturn:
        """
        Add the square scatterer to the provided axis as a polygon.

        Args:
            ax (Axis): The axis to which the scatterer will be added.
        """
        half_side = self.side_length / 2
        coordinates = [
            [self.coordinate.x - half_side, self.coordinate.y - half_side],
            [self.coordinate.x + half_side, self.coordinate.y - half_side],
            [self.coordinate.x + half_side, self.coordinate.y + half_side],
            [self.coordinate.x - half_side, self.coordinate.y + half_side]
        ]

        return ax.add_polygon(
            coordinates=coordinates,
            facecolor='lightgreen',
            edgecolor='green',
            label='square scatterer'
        )


@dataclass(config=config_dict)
class Circle(BaseComponent):
    """
    Represents a scatterer in a simulation grid.

    Attributes:
        grid (Grid): The grid of the simulation mesh.
        position (Tuple[float | str, float | str]): Starting position of the scatterer.
        epsilon_r (float): Relative permittivity inside the scatterer.
        radius (float): Radius of the scatterer.
    """
    grid: Grid
    position: Tuple[float | str, float | str]
    epsilon_r: float
    radius: float

    def build_mesh(self) -> NoReturn:
        """
        Build the permittivity mesh for the scatterer.
        """
        x0, y0 = self.position
        self.coordinate = self.grid.get_coordinate(x=x0, y=y0)

        distance_mesh = self.grid.get_distance_grid(x0=self.coordinate.x, y0=self.coordinate.y)

        self.idx = distance_mesh < self.radius

        self.idx = self.idx.T

        self.epsilon_r_mesh[self.idx] = self.epsilon_r

    def add_to_ax(self, ax: Axis) -> NoReturn:
        """
        Add the scatterer to the provided axis as a circle.

        Args:
            ax (Axis): The axis to which the scatterer will be added.
        """
        return ax.add_circle(
            position=(self.coordinate.x, self.coordinate.y),
            radius=self.radius,
            label='scatterer',
            facecolor='lightblue',
            edgecolor='blue'
        )


@dataclass(config=config_dict)
class Ellipse(BaseComponent):
    """
    Represents a scatterer in a simulation grid.

    Attributes:
        grid (Grid): The grid of the simulation mesh.
        position (Tuple[float | str, float | str]): Starting position of the scatterer.
        epsilon_r (float): Relative permittivity inside the scatterer.
        width (float):
        height (float):
        angle (float):
    """
    grid: Grid
    position: Tuple[float | str, float | str]
    width: float
    height: float
    epsilon_r: float
    angle: float = 0

    def build_mesh(self) -> NoReturn:
        """
        Build the permittivity mesh for the scatterer.
        """

        from shapely.geometry import Point
        from shapely.geometry.polygon import Polygon

        point = Point(0.5, 0.5)
        polygon = Polygon([(0, 0), (0, 1), (1, 1), (1, 0)])
        print(polygon.contains(point))

    def add_to_ax(self, ax: Axis) -> NoReturn:
        """
        Add the scatterer to the provided axis as a circle.

        Args:
            ax (Axis): The axis to which the scatterer will be added.
        """
        return ax.add_ellipse(
            position=(self.coordinate.x, self.coordinate.y),
            width=self.width,
            height=self.height,
            angle=self.angle,
            label='scatterer',
            facecolor='lightblue',
            edgecolor='blue'
        )


@dataclass
class Lens(BaseComponent):
    """
    Represents a lens in a simulation grid.

    Attributes:
        grid (Grid): The grid of the simulation mesh.
        position (Tuple[float | str, float | str]): Center position of the lens.
        epsilon_r (float): Relative permittivity inside the lens.
        radius_x (float): Radius of the lens along the x-axis.
        radius_y (float): Radius of the lens along the y-axis.
    """
    grid: Grid
    position: Tuple[float | str, float | str]
    epsilon_r: float
    radius_x: float
    radius_y: float

    def build_mesh(self) -> NoReturn:
        """
        Build the permittivity mesh for the lens.
        """
        x0, y0 = self.position
        self.coordinate = self.grid.get_coordinate(x=x0, y=y0)

        # Create a distance mesh for the lens
        x_mesh, y_mesh = numpy.meshgrid(self.grid.x_stamp, self.grid.y_stamp)
        distance_mesh = ((x_mesh - self.coordinate.x) / self.radius_x) ** 2 + ((y_mesh - self.coordinate.y) / self.radius_y) ** 2

        self.idx = distance_mesh <= 1

        self.epsilon_r_mesh[self.idx] = self.epsilon_r

    def add_to_ax(self, ax: Axis) -> NoReturn:
        """
        Add the lens to the provided axis as an ellipse.

        Args:
            ax (Axis): The axis to which the lens will be added.
        """
        coordinates = numpy.asarray([
            [self.coordinate.x - self.radius_x, self.coordinate.y - self.radius_y],
            [self.coordinate.x + self.radius_x, self.coordinate.y - self.radius_y],
            [self.coordinate.x + self.radius_x, self.coordinate.y + self.radius_y],
            [self.coordinate.x - self.radius_x, self.coordinate.y + self.radius_y]
        ])

        return ax.add_polygon(
            coordinates=coordinates,
            label='scatterer',
            facecolor='lightblue',
            edgecolor='blue'
        )
# -
