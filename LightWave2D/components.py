#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import NoReturn, Union, Tuple
from pydantic.dataclasses import dataclass
import numpy
from LightWave2D.physics import Physics
import matplotlib.pyplot as plt
import shapely.geometry as geo
from matplotlib.patches import PathPatch
from matplotlib import patches
import numpy as np
from matplotlib.path import Path
from matplotlib.collections import PatchCollection
from LightWave2D.grid import Grid
from shapely.affinity import scale, rotate


# Configuration dictionary for dataclasses
config_dict = {
    'kw_only': True,
    'extra': 'forbid',
    'slots': True,
    'arbitrary_types_allowed': True
}


@dataclass(kw_only=True, config=config_dict)
class BaseComponent():
    """
    Represents a generic component in a simulation grid.

    Attributes:
        grid (Grid): The simulation grid.
        facecolor (str): The color of the component's face.
        edgecolor (str): The color of the component's edge.
        alpha (float): Transparency level of the component.
        rotation (float): Rotation angle of the component.
    """
    grid: Grid
    facecolor: str = 'lightblue'
    edgecolor: str = 'blue'
    alpha: float = 0.3
    rotation: float = 0

    def __post_init__(self):
        x0, y0 = self.position
        self.coordinate = self.grid.get_coordinate(x=x0, y=y0)

        self.build_object()

    def build_object(self) -> NoReturn:
        """
        Build the permittivity mesh for the component.
        """
        self.epsilon_r_mesh = numpy.ones(self.grid.shape)  # Background permittivity

        self.compute_polygon()

        self.polygon = rotate(self.polygon, angle=self.rotation)

        self.polygon = self.polygon.intersection(self.grid.polygon)

        self.path = Path(self.polygon.exterior.coords)

        x_mesh, y_mesh = numpy.meshgrid(self.grid.x_stamp, self.grid.y_stamp)

        coordinates = numpy.c_[x_mesh.T.flatten(), y_mesh.T.flatten()]

        self.idx = self.path.contains_points(coordinates).astype(bool).reshape(self.epsilon_r_mesh.shape)

        self.epsilon_r_mesh[self.idx] = self.epsilon_r

    def add_to_ax(self, ax: plt.axis) -> PatchCollection:
        """
        Add the component to the provided axis.

        Args:
            ax (plt.Axes): The axis to which the component will be added.

        Returns:
            PatchCollection: The collection of patches added to the axis.
        """
        path = Path.make_compound_path(
            Path(np.asarray(self.polygon.exterior.coords)[:, :2]),
            *[Path(np.asarray(ring.coords)[:, :2]) for ring in self.polygon.interiors])

        patch = PathPatch(path, facecolor=self.facecolor, edgecolor=self.edgecolor, alpha=0.4)
        collection = PatchCollection([patch], facecolor=self.facecolor, edgecolor=self.edgecolor, alpha=self.alpha)

        ax.add_collection(collection, autolim=True)
        ax.autoscale_view()
        return collection

    def plot(self) -> NoReturn:
        """
        Plot the component.
        """
        figure, ax = plt.subplots(1, 1, figsize=(6, 6))
        ax.set_title('FDTD Simulation')
        ax.set_xlabel(r'x position [$\mu$m]')
        ax.set_xlabel(r'y position [$\mu$m]')
        ax.set_aspect('equal')

        self.add_to_ax(ax)
        ax.autoscale_view()

        plt.show()

    def add_to_mesh(self, epsilon_r_mesh: numpy.ndarray) -> NoReturn:
        """
        Add the component's permittivity to the provided mesh.

        Args:
            epsilon_r_mesh (np.ndarray): The permittivity mesh to be updated.
        """
        epsilon_r_mesh += self.epsilon_r_mesh

    def add_non_linear_effect_to_field(self, field: numpy.ndarray) -> NoReturn:
        """
        Add non-linear effects to the field.

        Args:
            field (np.ndarray): The field to which non-linear effects will be added.
        """
        chi_2 = 1e10

        field += self.idx * self.grid.dt**2 / (self.epsilon_r_mesh * Physics.epsilon_0 * Physics.mu_0) * chi_2 * field ** 2


@dataclass(config=config_dict)
class Waveguide(BaseComponent):
    """
    Represents a Waveguide scatterer in a simulation grid.

    Attributes:
        position (Tuple[Union[float, str], Union[float, str]]): The center position of the scatterer.
        epsilon_r (float): The relative permittivity inside the scatterer.
        side_length (float): The side length of the square scatterer.
    """
    position_0: Tuple[Union[float, str], Union[float, str]]
    position_1: Tuple[Union[float, str], Union[float, str]]
    width: float
    epsilon_r: float

    def __post_init__(self):
        x0, y0 = self.position_0
        x1, y1 = self.position_1
        self.coordinate_0 = self.grid.get_coordinate(x=x0, y=y0)
        self.coordinate_1 = self.grid.get_coordinate(x=x1, y=y1)

        self.build_object()

    def compute_polygon(self) -> Path:
        """
        Compute the polygon of the square scatterer.
        """
        line = geo.LineString(
            [(self.coordinate_0.x, self.coordinate_0.y), (self.coordinate_1.x, self.coordinate_1.y)]
        )

        self.polygon = line.buffer(self.width)


@dataclass(config=config_dict)
class Square(BaseComponent):
    """
    Represents a square scatterer in a simulation grid.

    Attributes:
        position (Tuple[Union[float, str], Union[float, str]]): The center position of the scatterer.
        epsilon_r (float): The relative permittivity inside the scatterer.
        side_length (float): The side length of the square scatterer.
    """
    position: Tuple[Union[float, str], Union[float, str]]
    epsilon_r: float
    side_length: float

    def compute_polygon(self) -> Path:
        """
        Compute the polygon of the square scatterer.
        """
        half_side = self.side_length / 2
        x_start, x_end = self.coordinate.x - half_side, self.coordinate.x + half_side
        y_start, y_end = self.coordinate.y - half_side, self.coordinate.y + half_side

        self.polygon = geo.Polygon([
            (x_start, y_start),
            (x_start, y_end),
            (x_end, y_end),
            (x_end, y_start)
        ]).convex_hull


@dataclass(config=config_dict)
class Circle(BaseComponent):
    """
    Represents a circular scatterer in a simulation grid.

    Attributes:
        position (Tuple[Union[float, str], Union[float, str]]): The center position of the scatterer.
        epsilon_r (float): The relative permittivity inside the scatterer.
        radius (float): The radius of the scatterer.
    """
    position: Tuple[Union[float, str], Union[float, str]]
    epsilon_r: float
    radius: float

    def compute_polygon(self) -> NoReturn:
        """
        Compute the polygon of the circular scatterer.
        """
        self.polygon = geo.Point(self.coordinate.x, self.coordinate.y).buffer(self.radius)


@dataclass(config=config_dict)
class Triangle(BaseComponent):
    """
    Represents a triangular scatterer in a simulation grid.

    Attributes:
        position (Tuple[Union[float, str], Union[float, str]]): The center position of the scatterer.
        epsilon_r (float): The relative permittivity inside the scatterer.
        side_length (float): The side length of the triangular scatterer.
    """
    position: Tuple[Union[float, str], Union[float, str]]
    epsilon_r: float
    side_length: float

    def compute_polygon(self) -> NoReturn:
        """
        Compute the polygon of the triangular scatterer.
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
        position (Tuple[Union[float, str], Union[float, str]]): The center position of the scatterer.
        width (float): The width of the ellipse.
        height (float): The height of the ellipse.
        epsilon_r (float): The relative permittivity inside the scatterer.
        resolution (float): The resolution of the ellipse.
    """
    position: Tuple[Union[float, str], Union[float, str]]
    width: float
    height: float
    epsilon_r: float
    resolution: float = 100

    def compute_polygon(self) -> NoReturn:
        """
        Compute the polygon of the elliptical scatterer.
        """
        ellipse_patch = patches.Ellipse(
            (self.coordinate.x, self.coordinate.y),
            width=self.resolution,
            height=self.resolution * self.height / self.width,
        )

        vertices = ellipse_patch.get_verts()
        polygon = geo.Polygon(vertices)

        self.polygon = scale(polygon, xfact=self.width / self.resolution, yfact=self.width / self.resolution)


@dataclass(config=config_dict)
class Grating(BaseComponent):
    """
    Represents a grating in a simulation grid.

    Attributes:
        position (Tuple[Union[float, str], Union[float, str]]): The starting position of the grating.
        epsilon_r (float): The relative permittivity inside the grating.
        period (float): The period of the grating.
        duty_cycle (float): The duty cycle of the grating.
        num_periods (int): The number of periods in the grating.
    """
    position: Tuple[Union[float, str], Union[float, str]]
    epsilon_r: float
    period: float
    duty_cycle: float
    num_periods: int

    def compute_polygon(self) -> NoReturn:
        """
        Compute the polygon of the grating.
        """
        bars = []
        for i in range(self.num_periods):
            x_start = self.coordinate.x + i * self.period
            x_end = x_start + self.duty_cycle * self.period
            bar = geo.box(x_start, self.coordinate.y - 0.5, x_end, self.coordinate.y + 0.5)
            bars.append(bar)

        self.polygon = geo.MultiPolygon(bars)


@dataclass(config=config_dict)
class RingResonator(BaseComponent):
    """
    Represents a ring resonator in a simulation grid.

    Attributes:
        position (Tuple[Union[float, str], Union[float, str]]): The center position of the ring resonator.
        epsilon_r (float): The relative permittivity inside the resonator.
        inner_radius (float): The inner radius of the ring.
        width (float): The width of the ring.
    """
    grid: Grid
    position: Tuple[Union[float, str], Union[float, str]]
    epsilon_r: float
    inner_radius: float
    width: float

    def compute_polygon(self) -> NoReturn:
        """
        Compute the polygon of the ring resonator.
        """
        inner_circle = geo.Point(self.coordinate.x, self.coordinate.y).buffer(self.inner_radius)
        outer_circle = geo.Point(self.coordinate.x, self.coordinate.y).buffer(self.inner_radius + self.width)
        self.polygon = outer_circle.difference(inner_circle)


@dataclass(config=config_dict)
class Lense(BaseComponent):
    """
    Represents a lens in a simulation grid.

    Attributes:
        position (Tuple[Union[float, str], Union[float, str]]): The center position of the lens.
        epsilon_r (float): The relative permittivity inside the lens.
        width (float): The width of the lens.
        curvature (float): The curvature of the lens (positive for convex, negative for concave).
    """
    position: Tuple[Union[float, str], Union[float, str]]
    epsilon_r: float
    width: float
    curvature: float

    def compute_polygon(self) -> NoReturn:
        """
        Compute the polygon of the lens.
        """
        # Create two arcs for the lens shape
        x0 = self.coordinate.x + self.curvature - self.width / 2
        x1 = self.coordinate.x - self.curvature + self.width / 2

        arc3 = geo.Point(x0, self.coordinate.y).buffer(self.curvature, resolution=100)
        arc4 = geo.Point(x1, self.coordinate.y).buffer(self.curvature, resolution=100)

        self.polygon = arc3.intersection(arc4)

# -
