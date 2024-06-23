#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Tuple, Union, NoReturn
from pydantic.dataclasses import dataclass
import numpy
from LightWave2D.grid import Grid
from LightWave2D.components.base_class import BaseComponent
from matplotlib.path import Path
import shapely.geometry as geo
from matplotlib import patches


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
    facecolor: str = 'lightblue'
    edgecolor: str = 'blue'

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
    facecolor: str = 'lightblue'
    edgecolor: str = 'blue'

    def compute_path(self) -> NoReturn:
        x0, y0 = self.position
        self.coordinate = self.grid.get_coordinate(x=x0, y=y0)

        half_side = self.side_length / 2
        self.x_start = (self.coordinate.x - half_side)
        self.x_end = (self.coordinate.x + half_side)
        self.y_start = (self.coordinate.y - half_side)
        self.y_end = (self.coordinate.y + half_side)

        p0 = geo.Point(self.x_start, self.y_start)
        p1 = geo.Point(self.x_start, self.y_end)
        p2 = geo.Point(self.x_end, self.y_start)
        p3 = geo.Point(self.x_end, self.y_end)

        self.polygon = geo.Polygon([p0, p1, p3, p2])

        self.path = Path(numpy.array(self.polygon.exterior.coords))


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
    facecolor: str = 'lightblue'

    def compute_path(self) -> NoReturn:
        x0, y0 = self.position
        self.coordinate = self.grid.get_coordinate(x=x0, y=y0)
        self.polygon = geo.Point(self.coordinate.x, self.coordinate.y).buffer(self.radius)
        self.path = Path(numpy.array(self.polygon.exterior.coords))


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
    facecolor: str = 'lightblue'
    edgecolor: str = 'blue'

    def compute_path(self) -> NoReturn:
        x0, y0 = self.position
        self.coordinate = self.grid.get_coordinate(x=x0, y=y0)

        polygon = patches.Ellipse(
            (self.coordinate.x, self.coordinate.y),
            width=self.width,
            height=self.height,
            angle=self.angle
        )

        vertices = polygon.get_verts()
        self.polygon = geo.Polygon(vertices)
        self.path = Path(numpy.array(self.polygon.exterior.coords))

# -
