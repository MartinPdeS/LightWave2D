#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy
from typing import Tuple, NoReturn, List, Union
from LightWave2D.utils import bresenham_line
from pydantic.dataclasses import dataclass
from matplotlib.path import Path
import shapely.geometry as geo
import matplotlib.pyplot as plt
from LightWave2D.physics import Physics
from matplotlib.patches import PathPatch
import matplotlib
from matplotlib.collections import PatchCollection
from LightWave2D.grid import Grid


# Configuration dictionary for dataclasses
config_dict = {
    'kw_only': True,
    'extra': 'forbid',
    'slots': True,
    'arbitrary_types_allowed': True
}


@dataclass(kw_only=True, config=config_dict)
class BaseSource():
    """
    Represents an elliptical scatterer in a simulation grid.

    Attributes:
        grid (Grid): The grid of the simulation mesh.
        angle (float): Rotation angle of the ellipse.
        facecolor (str): Color of the scatterer face.
        edgecolor (str): Color of the scatterer edge.
    """
    grid: Grid
    facecolor: str = 'red'
    edgecolor: str = 'red'
    alpha: float = 0.3
    rotation: float = 0

    def __post_init__(self):
        x0, y0 = self.position
        self.coordinate = self.grid.get_coordinate(x=x0, y=y0)

        self.build_object()

    def build_object(self) -> NoReturn:
        """
        Build the permittivity mesh for the square scatterer.
        """
        self.compute_polygon()

        self.path = Path(self.polygon.exterior.coords)

        self.path = self.path.transformed(matplotlib.transforms.Affine2D().rotate_around(self.coordinate.x, self.coordinate.y, self.rotation))

        x_mesh, y_mesh = numpy.meshgrid(self.grid.x_stamp, self.grid.y_stamp)

        coordinates = numpy.c_[x_mesh.T.flatten(), y_mesh.T.flatten()]

        self.idx = self.path.contains_points(coordinates).astype(bool).reshape(self.epsilon_r_mesh.shape)

    def add_to_ax(self, ax: plt.axis) -> PatchCollection:
        """
        Add the scatterer to the provided axis as a circle.

        Args:
            ax (Axis): The axis to which the scatterer will be added.
        """
        path = Path.make_compound_path(
            Path(numpy.asarray(self.polygon.exterior.coords)[:, :2]),
            *[Path(numpy.asarray(ring.coords)[:, :2]) for ring in self.polygon.interiors])

        patch = PathPatch(path, color=self.facecolor, edgecolor=self.edgecolor, alpha=0.4)
        collection = PatchCollection([patch], color=self.facecolor, edgecolor=self.edgecolor, alpha=self.alpha)

        ax.add_collection(collection, autolim=True)
        ax.autoscale_view()
        return collection

    def plot(self) -> NoReturn:
        figure, ax = plt.subplots(1, 1, figsize=(6, 6))
        ax.set_title('FDTD Simulation')
        ax.set_xlabel(r'x position [$\mu$m]')
        ax.set_xlabel(r'y position [$\mu$m]')
        ax.set_aspect('equal')

        self.add_to_ax(ax)
        ax.autoscale_view()

        plt.show()


@dataclass(kw_only=True, config=config_dict)
class PointSource(BaseSource):
    """
    Represents a point source in a 2D light wave simulation.

    Attributes:
        wavelength (float): Wavelength of the source.
        position (tuple): Position (x, y) of the source.
        amplitude (float): Amplitude of the electric field, default is 1.0.
    """
    wavelength: Union[float | List[float] | numpy.ndarray]
    position: Tuple[float | str, float | str]
    amplitude: float = 1.0
    facecolor: str = 'red'
    edgecolor: str = 'red'

    def __post_init__(self):
        self.wavelength = numpy.atleast_1d(self.wavelength)
        self.frequency = Physics.c / self.wavelength
        self.omega = 2 * numpy.pi * self.frequency
        x, y = self.position
        self.p0 = self.grid.get_coordinate(x=x, y=y)
        self.polygon = geo.Point(self.p0.x, self.p0.y)
        self.path = Path(self.polygon.coords)

    def add_to_ax(self, ax: plt.Axes) -> NoReturn:
        """
        Add the point source to the provided axis as a scatter point.

        Args:
            ax (plt.Axes): The axis to which the point source will be added.
        """
        ax.scatter(
            self.p0.x,
            self.p0.y,
            color=self.facecolor,
            label='source'
        )

    def add_source_to_field(self, field: numpy.ndarray, time: float) -> NoReturn:
        """
        Add the source's effect to the simulation field.

        Args:
            field (numpy.ndarray): The simulation field to which the source's effect will be added.
            time (float): The current simulation time.
        """
        field[self.p0.x_index, self.p0.y_index] = self.amplitude / len(self.omega) * numpy.sin(self.omega * time).sum()


@dataclass(kw_only=True, config=config_dict)
class PointImpulsion(BaseSource):
    """
    Represents a point source in a 2D light wave simulation.

    Attributes:
        wavelength (float): Wavelength of the source.
        position (tuple): Position (x, y) of the source.
        amplitude (float): Amplitude of the electric field, default is 1.0.
    """
    duration: float
    position: Tuple[float | str, float | str]
    delay: float = 0
    amplitude: float = 1.0
    facecolor: str = 'red'
    edgecolor: str = 'red'

    def __post_init__(self):
        x, y = self.position
        self.p0 = self.grid.get_coordinate(x=x, y=y)
        self.polygon = geo.Point(self.p0.x, self.p0.y)
        self.path = Path(self.polygon.coords)

    def add_to_ax(self, ax: plt.Axes) -> NoReturn:
        """
        Add the point source to the provided axis as a scatter point.

        Args:
            ax (plt.Axes): The axis to which the point source will be added.
        """
        ax.scatter(
            self.p0.x,
            self.p0.y,
            color=self.facecolor,
            label='source'
        )

    def add_source_to_field(self, field: numpy.ndarray, time: float) -> NoReturn:
        """
        Add the source's effect to the simulation field.

        Args:
            field (numpy.ndarray): The simulation field to which the source's effect will be added.
            time (float): The current simulation time.
        """
        source_field = numpy.exp(-((time - self.delay) / self.duration) ** 2)

        field[self.p0.x_index, self.p0.y_index] = self.amplitude * source_field


@dataclass(kw_only=True, config=config_dict)
class LineSource(BaseSource):
    """
    Represents a line source in a 2D light wave simulation.

    Attributes:
        wavelength (float): Wavelength of the source.
        point_0 (Tuple[float, float]): Starting position (x, y) of the source.
        point_1 (Tuple[float, float]): Ending position (x, y) of the source.
        amplitude (float): Amplitude of the electric field, default is 1.0.
    """
    wavelength: float
    position_0: Tuple[float | str, float | str]
    position_1: Tuple[float | str, float | str]
    amplitude: float = 1.0

    def __post_init__(self):
        self.frequency = Physics.c / self.wavelength
        self.omega = 2 * numpy.pi * self.frequency
        self.build_object()

    def build_object(self) -> NoReturn:
        """
        Build the line source object and calculate the line's coordinates.
        """
        self.p0 = self.grid.get_coordinate(x=self.position_0[0], y=self.position_0[1])
        self.p1 = self.grid.get_coordinate(x=self.position_1[0], y=self.position_1[1])

        position = bresenham_line(
            x0=self.p0.x_index,
            y0=self.p0.y_index,
            x1=self.p1.x_index,
            y1=self.p1.y_index
        )

        rows, cols = zip(*position.T)
        self.slice_indexes = rows, cols

        p0 = geo.Point(self.p0.x, self.p0.y)
        p1 = geo.Point(self.p1.x, self.p1.y)
        self.polygon = geo.LineString((p0, p1))

    def add_to_ax(self, ax: plt.axis) -> NoReturn:
        """
        Add the scatterer to the provided axis as a circle.

        Args:
            ax (Axis): The axis to which the scatterer will be added.
        """
        ax.plot(
            self.polygon.xy[0],
            self.polygon.xy[1],
            color=self.facecolor,
            label='source'
        )

    def add_source_to_field(self, field: numpy.ndarray, time: float) -> NoReturn:
        """
        Add the source's effect to the simulation field.

        Args:
            field (numpy.ndarray): The simulation field to which the source's effect will be added.
            time (float): The current simulation time.
        """
        rows, cols = self.slice_indexes
        field[rows, cols] = self.amplitude * numpy.sin(self.omega * time)
