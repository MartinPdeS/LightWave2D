#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Tuple, Union, NoReturn
from pydantic.dataclasses import dataclass
import numpy as np
from LightWave2D.grid import Grid
from LightWave2D.components.base_class import BaseComponent
from matplotlib.path import Path
import shapely.geometry as geo
from matplotlib import patches
from shapely.affinity import scale

# Configuration dictionary for dataclasses
config_dict = {
    'kw_only': True,
    'extra': 'forbid',
    'slots': True,
    'arbitrary_types_allowed': True
}


@dataclass(config=config_dict)
class Square(BaseComponent):
    """
    Represents a square scatterer in a simulation grid.

    Attributes:
        position (Tuple[Union[float, str], Union[float, str]]): Starting position of the scatterer (center of the square).
        epsilon_r (float): Relative permittivity inside the scatterer.
        side_length (float): Side length of the square scatterer.
    """
    position: Tuple[Union[float, str], Union[float, str]]
    epsilon_r: float
    side_length: float

    def compute_polygon(self) -> Path:
        """
        Compute the path of the square scatterer.
        """
        half_side = self.side_length / 2
        x_start, x_end = self.coordinate.x - half_side, self.coordinate.x + half_side
        y_start, y_end = self.coordinate.y - half_side, self.coordinate.y + half_side

        self.polygon = geo.Polygon([
            (x_start, y_start),
            (x_start, y_end),
            (x_end, y_end),
            (x_end, y_start)
        ])


@dataclass(config=config_dict)
class Circle(BaseComponent):
    """
    Represents a circular scatterer in a simulation grid.

    Attributes:
        position (Tuple[Union[float, str], Union[float, str]]): Starting position of the scatterer.
        epsilon_r (float): Relative permittivity inside the scatterer.
        radius (float): Radius of the scatterer.
    """
    position: Tuple[Union[float, str], Union[float, str]]
    epsilon_r: float
    radius: float

    def compute_polygon(self) -> Path:
        """
        Compute the path of the circular scatterer.
        """
        self.polygon = geo.Point(self.coordinate.x, self.coordinate.y).buffer(self.radius)


@dataclass(config=config_dict)
class Triangle(BaseComponent):
    """
    Represents a triangular scatterer in a simulation grid.

    Attributes:
        position (Tuple[Union[float, str], Union[float, str]]): Starting position of the scatterer (center of the triangle).
        epsilon_r (float): Relative permittivity inside the scatterer.
        side_length (float): Side length of the triangle.
    """
    position: Tuple[Union[float, str], Union[float, str]]
    epsilon_r: float
    side_length: float

    def compute_polygon(self) -> NoReturn:
        """
        Compute the path of the triangular scatterer.
        """
        height = (np.sqrt(3) / 2) * self.side_length

        # Vertices of an equilateral triangle centered at (coordinate.x, coordinate.y)
        p0 = (self.coordinate.x - self.side_length / 2, self.coordinate.y - height / 3)
        p1 = (self.coordinate.x + self.side_length / 2, self.coordinate.y - height / 3)
        p2 = (self.coordinate.x, self.coordinate.y + 2 * height / 3)

        self.polygon = geo.Polygon([p0, p1, p2])


@dataclass(config=config_dict)
class Ellipse(BaseComponent):
    """
    Represents an elliptical scatterer in a simulation grid.

    Attributes:
        position (Tuple[Union[float, str], Union[float, str]]): Starting position of the scatterer.
        width (float): Width of the ellipse.
        height (float): Height of the ellipse.
        epsilon_r (float): Relative permittivity inside the scatterer.
        resolution (float): Resolution of the ellipse.
    """
    position: Tuple[Union[float, str], Union[float, str]]
    width: float
    height: float
    epsilon_r: float
    resolution: float = 100

    def compute_polygon(self) -> Path:
        """
        Compute the path of the elliptical scatterer.
        """
        ellipse_patch = patches.Ellipse(
            (self.coordinate.x, self.coordinate.y),
            width=self.resolution,
            height=self.resolution * self.height / self.width,
        )

        vertices = ellipse_patch.get_verts()
        polygon = geo.Polygon(vertices)

        self.polygon = scale(polygon, xfact=self.width / self.resolution, yfact=self.width / self.resolution)
