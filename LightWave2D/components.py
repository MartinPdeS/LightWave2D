#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Tuple
from pydantic.dataclasses import dataclass
import numpy as np
import matplotlib.pyplot as plt
import shapely.geometry as geo
from matplotlib.patches import PathPatch
from matplotlib import patches
from matplotlib.path import Path
from matplotlib.collections import PatchCollection
from shapely.affinity import scale, rotate
from TypedUnit import AnyUnit, Length, ureg

from LightWave2D.grid import Grid
from LightWave2D.utils import config_dict


@dataclass(config=config_dict, kw_only=True)
class BaseComponent:
    """
    Represents a generic component in a simulation grid.

    Parameters
    ----------
    grid : Grid
        The simulation grid.
    facecolor : str
        The color of the component's face (default is 'lightblue').
    edgecolor : str
        The color of the component's edge (default is 'blue').
    alpha : float
        Transparency level of the component (default is 0.3).
    rotation : float
        Rotation angle of the component (default is 0 degrees).
    sigma : float
        Conductivity of the component (default is 0).
    """
    grid: Grid
    facecolor: str = 'lightblue'
    edgecolor: str = 'blue'
    alpha: float = 0.3
    rotation: float = 0
    sigma: AnyUnit = 0 * (ureg.siemens / ureg.meter)

    def __post_init__(self):
        """
        Initialize the component by building its object and computing the coordinates.
        """
        x0, y0 = self.position
        self.coordinate = self.grid.get_coordinate(x=x0, y=y0)
        self.build_object()

    def build_object(self) -> None:
        """
        Build the permittivity mesh for the component.
        """
        self.epsilon_r_mesh = np.ones(self.grid.shape)  # Background permittivity
        self.compute_polygon()
        self.polygon = rotate(self.polygon, angle=self.rotation)
        self.polygon = self.polygon.intersection(self.grid.polygon)
        self.path = Path(self.polygon.exterior.coords)
        coordinates = np.c_[self.grid.x_mesh.T.flatten().to('meter').magnitude, self.grid.y_mesh.T.flatten().to('meter').magnitude]
        self.idx = self.path.contains_points(coordinates).astype(bool).reshape(self.epsilon_r_mesh.shape)

    def add_to_ax(self, ax: plt.Axes) -> PatchCollection:
        """
        Add the component to the provided axis.

        Parameters
        ----------
        ax : plt.Axes
            The axis to which the component will be added.

        Returns
        -------
        PatchCollection
            The collection of patches added to the axis.
        """
        path = Path.make_compound_path(
            Path(np.asarray(self.polygon.exterior.coords)[:, :2]),
            *[Path(np.asarray(ring.coords)[:, :2]) for ring in self.polygon.interiors]
        )

        patch = PathPatch(path, facecolor=self.facecolor, edgecolor=self.edgecolor, alpha=0.4)
        collection = PatchCollection([patch], facecolor=self.facecolor, edgecolor=self.edgecolor, alpha=self.alpha)

        ax.add_collection(collection, autolim=True)
        ax.autoscale_view()
        return collection

    def plot(self) -> None:
        """
        Plot the component.
        """
        figure, ax = plt.subplots(1, 1, figsize=(6, 6))
        ax.set_title('FDTD Simulation')
        ax.set_xlabel(r'x position [$\mu$m]')
        ax.set_ylabel(r'y position [$\mu$m]')
        ax.set_aspect('equal')
        self.add_to_ax(ax)
        ax.autoscale_view()
        plt.show()

    def add_to_epsilon_r_mesh(self, epsilon_r_mesh: np.ndarray) -> None:
        """
        Add the component's permittivity to the provided mesh.

        Parameters
        ----------
        epsilon_r_mesh : np.ndarray
            The permittivity mesh to be updated.
        """
        epsilon_r_mesh[self.idx] = self.epsilon_r

    def add_to_sigma_mesh(self, sigma_mesh: np.ndarray) -> None:
        """
        Add the component's sigma to the provided mesh.

        Parameters
        ----------
        sigma_mesh : np.ndarray
            The permittivity mesh to be updated.
        """
        sigma_mesh[self.idx] = self.sigma

    def add_non_linear_effect_to_field(self, field: np.ndarray) -> None:
        """
        Add non-linear effects to the field.

        Parameters
        ----------
        field : np.ndarray
            The field to which non-linear effects will be added.
        """
        chi_3 = 1e-8  # Third-order non-linear susceptibility (example value)
        intensity = np.abs(field) ** 2
        nonlinear_term = chi_3 * intensity * field
        return field + self.grid.dt * nonlinear_term


@dataclass(config=config_dict, kw_only=True)
class Waveguide(BaseComponent):
    """
    Represents a waveguide scatterer in a simulation grid.

    Parameters
    ----------
    position_0 : Tuple[Length | str, Length | str]
        The starting position of the waveguide.
    position_1 : Tuple[Length | str, Length | str]
        The ending position of the waveguide.
    width : Length | str
        The width of the waveguide.
    epsilon_r : float
        The relative permittivity inside the waveguide.
    """
    position_0: Tuple[Length | str, Length | str]
    position_1: Tuple[Length | str, Length | str]
    width: Length | str
    epsilon_r: float

    def __post_init__(self):
        """
        Initialize the waveguide by computing its coordinates and building its object.
        """
        x0, y0 = self.position_0
        x1, y1 = self.position_1
        self.coordinate_0 = self.grid.get_coordinate(x=x0, y=y0)
        self.coordinate_1 = self.grid.get_coordinate(x=x1, y=y1)
        self.build_object()

    def compute_polygon(self) -> Path:
        """
        Compute the polygon of the waveguide.
        """
        line = geo.LineString(
            [
                (self.coordinate_0.x.to('meter').magnitude, self.coordinate_0.y.to('meter').magnitude),
                (self.coordinate_1.x.to('meter').magnitude, self.coordinate_1.y.to('meter').magnitude)
            ]
        )
        self.polygon = line.buffer(self.width.to('meter').magnitude / 2)


@dataclass(config=config_dict)
class Square(BaseComponent):
    """
    Represents a square scatterer in a simulation grid.

    Parameters
    ----------
    position : Tuple[Union[float, str], Union[float, str]]
        The center position of the scatterer.
    epsilon_r : float
        The relative permittivity inside the scatterer.
    side_length : Length
        The side length of the square scatterer.
    """
    position: Tuple[Length | str, Length | str]
    epsilon_r: float
    side_length: Length

    def compute_polygon(self) -> Path:
        """
        Compute the polygon of the square scatterer.
        """
        half_side = self.side_length / 2
        x_start, x_end = self.coordinate.x - half_side, self.coordinate.x + half_side
        y_start, y_end = self.coordinate.y - half_side, self.coordinate.y + half_side

        self.polygon = geo.Polygon([
            (x_start.to('meter').magnitude, y_start.to('meter').magnitude),
            (x_start.to('meter').magnitude, y_end.to('meter').magnitude),
            (x_end.to('meter').magnitude, y_end.to('meter').magnitude),
            (x_end.to('meter').magnitude, y_start.to('meter').magnitude)
        ]).convex_hull


@dataclass(config=config_dict, kw_only=True)
class Circle(BaseComponent):
    """
    Represents a circular scatterer in a simulation grid.

    Parameters
    ----------
    position : Tuple[Length | str, Length | str]
        The center position of the scatterer.
    epsilon_r : float
        The relative permittivity inside the scatterer.
    radius : float
        The radius of the scatterer.
    """
    position: Tuple[Length | str, Length | str]
    epsilon_r: float
    radius: Length

    def compute_polygon(self) -> None:
        """
        Compute the polygon of the circular scatterer.
        """
        self.polygon = geo.Point(self.coordinate.x.to('meter').magnitude, self.coordinate.y.to('meter').magnitude).buffer(self.radius.to('meter').magnitude)


@dataclass(config=config_dict, kw_only=True)
class Triangle(BaseComponent):
    """
    Represents a triangular scatterer in a simulation grid.

    Parameters
    ----------
    position : Tuple[Length | str, Length | str]
        The center position of the scatterer.
    epsilon_r : float
        The relative permittivity inside the scatterer.
    side_length : Length
        The side length of the triangular scatterer.
    """
    position: Tuple[Length | str, Length | str]
    epsilon_r: float
    side_length: Length

    def compute_polygon(self) -> None:
        """
        Compute the polygon of the triangular scatterer.
        """
        height = (np.sqrt(3) / 2) * self.side_length

        # Vertices of an equilateral triangle centered at (coordinate.x, coordinate.y)
        p0 = (self.coordinate.x - self.side_length / 2, self.coordinate.y - height / 3)
        p1 = (self.coordinate.x + self.side_length / 2, self.coordinate.y - height / 3)
        p2 = (self.coordinate.x, self.coordinate.y + 2 * height / 3)

        self.polygon = geo.Polygon([p0, p1, p2])


@dataclass(config=config_dict, kw_only=True)
class Ellipse(BaseComponent):
    """
    Represents an elliptical scatterer in a simulation grid.

    Parameters
    ----------
    position : Tuple[Length | str, Length | str]
        The center position of the scatterer.
    width : Length | str
        The width of the ellipse.
    height : Length | str
        The height of the ellipse.
    epsilon_r : float
        The relative permittivity inside the scatterer.
    resolution : float, optional
        The resolution of the ellipse (default is 100).
    """
    position: Tuple[Length | str, Length | str]
    width: Length | str
    height: Length | str
    epsilon_r: float
    resolution_factor: int = 10e6

    def compute_polygon(self) -> None:
        """
        Compute the polygon of the elliptical scatterer.
        """
        ellipse_patch = patches.Ellipse(
            (self.coordinate.x.to('meter').magnitude, self.coordinate.y.to('meter').magnitude),
            width=self.width.to('meter').magnitude * self.resolution_factor,
            height=self.height.to('meter').magnitude * self.resolution_factor,
        )

        vertices = ellipse_patch.get_verts()

        self.polygon = geo.Polygon(vertices)

        self.polygon = scale(self.polygon, xfact=1 / self.resolution_factor, yfact=1 / self.resolution_factor)


@dataclass(config=config_dict, kw_only=True)
class Grating(BaseComponent):
    """
    Represents a grating in a simulation grid.

    Parameters
    ----------
    position : Tuple[Length | str, Length | str]
        The starting position of the grating.
    epsilon_r : float
        The relative permittivity inside the grating.
    period : float
        The period of the grating.
    duty_cycle : float
        The duty cycle of the grating.
    num_periods : int
        The number of periods in the grating.
    """
    position: Tuple[Length | str, Length | str]
    epsilon_r: float
    period: float
    duty_cycle: float
    num_periods: int

    def compute_polygon(self) -> None:
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


@dataclass(config=config_dict, kw_only=True)
class RingResonator(BaseComponent):
    """
    Represents a ring resonator in a simulation grid.

    Parameters
    ----------
    position : Tuple[Length | str, Length | str]
        The center position of the ring resonator.
    epsilon_r : float
        The relative permittivity inside the resonator.
    inner_radius : float
        The inner radius of the ring.
    width : float
        The width of the ring.
    """
    grid: Grid
    position: Tuple[Length | str, Length | str]
    epsilon_r: float
    inner_radius: Length
    width: Length

    def compute_polygon(self) -> None:
        """
        Compute the polygon of the ring resonator.
        """
        inner_circle = geo.Point(self.coordinate.x.to('meter').magnitude, self.coordinate.y.to('meter').magnitude).buffer(self.inner_radius.to('meter').magnitude)
        outer_circle = geo.Point(self.coordinate.x.to('meter').magnitude, self.coordinate.y.to('meter').magnitude).buffer(self.inner_radius.to('meter').magnitude + self.width.to('meter').magnitude)
        self.polygon = outer_circle.difference(inner_circle)


@dataclass(config=config_dict, kw_only=True)
class Lense(BaseComponent):
    """
    Represents a lens in a simulation grid.

    Parameters
    ----------
    position : Tuple[Length | str, Length | str]
        The center position of the lens.
    epsilon_r : float
        The relative permittivity inside the lens.
    width : Length | str
        The width of the lens.
    curvature : Length | str
        The curvature of the lens (positive for convex, negative for concave).
    """
    position: Tuple[Length | str, Length | str]
    epsilon_r: float
    width: Length | str
    curvature: Length | str

    def compute_polygon(self) -> None:
        """
        Compute the polygon of the lens.
        """
        # Create two arcs for the lens shape
        x0 = self.coordinate.x + self.curvature - self.width / 2
        x1 = self.coordinate.x - self.curvature + self.width / 2

        arc3 = geo.Point(x0.to('meter').magnitude, self.coordinate.y.to('meter').magnitude).buffer(self.curvature.to('meter').magnitude, resolution=100)
        arc4 = geo.Point(x1.to('meter').magnitude, self.coordinate.y.to('meter').magnitude).buffer(self.curvature.to('meter').magnitude, resolution=100)

        self.polygon = arc3.intersection(arc4)
