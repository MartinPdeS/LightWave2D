#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Tuple, NoReturn
import numpy as np
from LightWave2D.grid import Grid
from LightWave2D.utils import bresenham_line
from pydantic.dataclasses import dataclass
from LightWave2D.components.base_class import BaseComponent
from matplotlib.path import Path
import shapely.geometry as geo
import matplotlib.pyplot as plt
from LightWave2D.physics import Physics

config_dict = {
    'kw_only': True,
    'slots': True,
    'extra': 'forbid',
    'arbitrary_types_allowed': True
}


@dataclass(config=config_dict)
class PointSource(BaseComponent):
    """
    Represents a point source in a 2D light wave simulation.

    Attributes:
        grid (Grid): The grid of the simulation mesh.
        wavelength (float): Wavelength of the source.
        position (tuple): Position (x, y) of the source.
        amplitude (float): Amplitude of the electric field, default is 1.0.
        facecolor (str): Color for the source's face, default is 'red'.
        edgecolor (str): Color for the source's edge, default is 'red'.
    """
    grid: Grid
    wavelength: float
    position: Tuple[float | str, float | str]
    amplitude: float = 1.0
    facecolor: str = 'red'
    edgecolor: str = 'red'

    def __post_init__(self):
        self.frequency = Physics.c / self.wavelength
        self.omega = 2 * np.pi * self.frequency
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
        ax.scatter(self.p0.x, self.p0.y, color=self.facecolor)

    def add_source_to_field(self, field: np.ndarray, time: float) -> NoReturn:
        """
        Add the source's effect to the simulation field.

        Args:
            field (np.ndarray): The simulation field to which the source's effect will be added.
            time (float): The current simulation time.
        """
        field[self.p0.x_index, self.p0.y_index] += self.amplitude * np.sin(self.omega * time)


@dataclass(config=config_dict)
class LineSource(BaseComponent):
    """
    Represents a line source in a 2D light wave simulation.

    Attributes:
        grid (Grid): The grid of the simulation mesh.
        wavelength (float): Wavelength of the source.
        point_0 (Tuple[float, float]): Starting position (x, y) of the source.
        point_1 (Tuple[float, float]): Ending position (x, y) of the source.
        amplitude (float): Amplitude of the electric field, default is 1.0.
        facecolor (str): Color for the source's face, default is 'red'.
        edgecolor (str): Color for the source's edge, default is 'red'.
    """
    grid: Grid
    wavelength: float
    point_0: Tuple[float | str, float | str]
    point_1: Tuple[float | str, float | str]
    amplitude: float = 1.0
    facecolor: str = 'red'
    edgecolor: str = 'red'

    def __post_init__(self):
        self.frequency = Physics.c / self.wavelength
        self.omega = 2 * np.pi * self.frequency
        self.build_object()

    def build_object(self) -> NoReturn:
        """
        Build the line source object and calculate the line's coordinates.
        """
        self.p0 = self.grid.get_coordinate(x=self.point_0[0], y=self.point_0[1])
        self.p1 = self.grid.get_coordinate(x=self.point_1[0], y=self.point_1[1])

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
        ax.plot(self.polygon.xy[0], self.polygon.xy[1], color=self.facecolor)

    def add_source_to_field(self, field: np.ndarray, time: float) -> NoReturn:
        """
        Add the source's effect to the simulation field.

        Args:
            field (np.ndarray): The simulation field to which the source's effect will be added.
            time (float): The current simulation time.
        """
        rows, cols = self.slice_indexes
        field[rows, cols] += self.amplitude * np.sin(self.omega * time)
