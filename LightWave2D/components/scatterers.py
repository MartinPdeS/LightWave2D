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
        grid (Grid): The grid of the simulation mesh.
        position (Tuple[Union[float, str], Union[float, str]]): Starting position of the scatterer (center of the square).
        epsilon_r (float): Relative permittivity inside the scatterer.
        side_length (float): Side length of the square scatterer.
        facecolor (str): Color of the scatterer face.
        edgecolor (str): Color of the scatterer edge.
    """
    grid: Grid
    position: Tuple[Union[float, str], Union[float, str]]
    epsilon_r: float
    side_length: float
    facecolor: str = 'lightblue'
    edgecolor: str = 'blue'
    rotation: float = 0

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

        # return Path(np.array(polygon.exterior.coords))


@dataclass(config=config_dict)
class Grating(BaseComponent):
    """
    Represents a grating in a simulation grid.

    Attributes:
        grid (Grid): The grid of the simulation mesh.
        position (Tuple[Union[float, str], Union[float, str]]): Starting position of the grating.
        epsilon_r (float): Relative permittivity inside the grating.
        period (float): Period of the grating.
        duty_cycle (float): Duty cycle of the grating (fraction of period occupied by the grating material).
        num_periods (int): Number of grating periods.
        facecolor (str): Color of the grating face.
        edgecolor (str): Color of the grating edge.
    """
    grid: Grid
    position: Tuple[Union[float, str], Union[float, str]]
    epsilon_r: float
    period: float
    duty_cycle: float
    num_periods: int
    facecolor: str = 'lightblue'
    edgecolor: str = 'blue'
    rotation: float = 0

    def compute_polygon(self) -> NoReturn:
        """
        Compute the path of the grating.
        """
        bars = []
        for i in range(self.num_periods):
            x_start = self.coordinate.x + i * self.period
            x_end = x_start + self.duty_cycle * self.period
            bar = geo.box(x_start, self.coordinate.y - 0.5, x_end, self.coordinate.y + 0.5)
            bars.append(bar)

        self.polygon = geo.MultiPolygon(bars)
        # return Path(np.array(grating_polygon.exterior.coords))


@dataclass(config=config_dict)
class RingResonator(BaseComponent):
    """
    Represents a ring resonator in a simulation grid.

    Attributes:
        grid (Grid): The grid of the simulation mesh.
        position (Tuple[Union[float, str], Union[float, str]]): Starting position of the resonator (center of the ring).
        epsilon_r (float): Relative permittivity inside the resonator.
        inner_radius (float): Inner radius of the ring.
        outer_radius (float): Outer radius of the ring.
        facecolor (str): Color of the resonator face.
        edgecolor (str): Color of the resonator edge.
    """
    grid: Grid
    position: Tuple[Union[float, str], Union[float, str]]
    epsilon_r: float
    inner_radius: float
    outer_radius: float
    facecolor: str = 'lightblue'
    edgecolor: str = 'blue'
    rotation: float = 0

    def compute_polygon(self) -> Path:
        """
        Compute the path of the ring resonator.
        """
        outer_circle = geo.Point(self.coordinate.x, self.coordinate.y).buffer(self.outer_radius)
        inner_circle = geo.Point(self.coordinate.x, self.coordinate.y).buffer(self.inner_radius)
        self.polygon = outer_circle.difference(inner_circle)

        # return Path(np.array(self.polygon.exterior.coords))


@dataclass(config=config_dict)
class Circle(BaseComponent):
    """
    Represents a circular scatterer in a simulation grid.

    Attributes:
        grid (Grid): The grid of the simulation mesh.
        position (Tuple[Union[float, str], Union[float, str]]): Starting position of the scatterer.
        epsilon_r (float): Relative permittivity inside the scatterer.
        radius (float): Radius of the scatterer.
        facecolor (str): Color of the scatterer face.
    """
    grid: Grid
    position: Tuple[Union[float, str], Union[float, str]]
    epsilon_r: float
    radius: float
    facecolor: str = 'lightblue'
    rotation: float = 0

    def compute_polygon(self) -> Path:
        """
        Compute the path of the circular scatterer.
        """
        self.polygon = geo.Point(self.coordinate.x, self.coordinate.y).buffer(self.radius)
        # return Path(np.array(self.polygon.exterior.coords))


@dataclass(config=config_dict)
class Triangle(BaseComponent):
    """
    Represents a triangular scatterer in a simulation grid.

    Attributes:
        grid (Grid): The grid of the simulation mesh.
        position (Tuple[Union[float, str], Union[float, str]]): Starting position of the scatterer (center of the triangle).
        epsilon_r (float): Relative permittivity inside the scatterer.
        side_length (float): Side length of the triangle.
        facecolor (str): Color of the scatterer face.
        edgecolor (str): Color of the scatterer edge.
    """
    grid: Grid
    position: Tuple[Union[float, str], Union[float, str]]
    epsilon_r: float
    side_length: float
    facecolor: str = 'lightblue'
    edgecolor: str = 'blue'
    rotation: float = 0

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

        # return Path(np.array(self.polygon.exterior.coords))


@dataclass(config=config_dict)
class Lense(BaseComponent):
    """
    Represents a lens in a simulation grid.

    Attributes:
        grid (Grid): The grid of the simulation mesh.
        position (Tuple[Union[float, str], Union[float, str]]): Starting position of the lens (center of the lens).
        epsilon_r (float): Relative permittivity inside the lens.
        radius (float): Radius of the lens.
        curvature (float): Curvature of the lens (positive for convex, negative for concave).
        facecolor (str): Color of the lens face.
        edgecolor (str): Color of the lens edge.
    """
    grid: Grid
    position: Tuple[Union[float, str], Union[float, str]]
    epsilon_r: float
    width: float
    curvature: float
    facecolor: str = 'lightblue'
    edgecolor: str = 'blue'
    rotation: float = 0

    def compute_polygon(self) -> Path:
        """
        Compute the path of the lens.
        """
        # Create two arcs for the lens shape
        x0 = self.coordinate.x + self.curvature - self.width / 2
        x1 = self.coordinate.x - self.curvature + self.width / 2

        arc3 = geo.Point(x0, self.coordinate.y).buffer(self.curvature, resolution=100)
        arc4 = geo.Point(x1, self.coordinate.y).buffer(self.curvature, resolution=100)

        self.polygon = arc3.intersection(arc4)

        # return Path(self.polygon.exterior.coords)


@dataclass(config=config_dict)
class Ellipse(BaseComponent):
    """
    Represents an elliptical scatterer in a simulation grid.

    Attributes:
        grid (Grid): The grid of the simulation mesh.
        position (Tuple[Union[float, str], Union[float, str]]): Starting position of the scatterer.
        width (float): Width of the ellipse.
        height (float): Height of the ellipse.
        epsilon_r (float): Relative permittivity inside the scatterer.
        angle (float): Rotation angle of the ellipse.
        facecolor (str): Color of the scatterer face.
        edgecolor (str): Color of the scatterer edge.
        resolution (int): Resolution of the ellipse.
    """
    grid: Grid
    position: Tuple[Union[float, str], Union[float, str]]
    width: float
    height: float
    epsilon_r: float
    angle: float = 0
    facecolor: str = 'lightblue'
    edgecolor: str = 'blue'
    resolution: int = 100
    rotation: float = 0

    def compute_polygon(self) -> Path:
        """
        Compute the path of the elliptical scatterer.
        """
        ellipse_patch = patches.Ellipse(
            (self.coordinate.x, self.coordinate.y),
            width=self.resolution,
            height=self.resolution * self.height / self.width,
            angle=self.angle
        )

        vertices = ellipse_patch.get_verts()
        polygon = geo.Polygon(vertices)
        self.polygon = scale(polygon, xfact=self.width / self.resolution, yfact=self.width / self.resolution)

        # return Path(np.array(self.polygon.exterior.coords))
