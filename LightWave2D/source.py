#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Tuple, NoReturn
import numpy
from LightWave2D.grid import Grid
from LightWave2D.utils import bresenham_line
from pydantic.dataclasses import dataclass
from LightWave2D.components.base_class import BaseComponent
from matplotlib.path import Path
import shapely.geometry as geo
import matplotlib.pyplot as plt

config_dict = dict(
    kw_only=True,
    slots=True,
    extra='forbid',
    arbitrary_types_allowed=True
)


@dataclass(config=config_dict)
class PointSource(BaseComponent):
    grid: Grid
    """ The grid of the simulation mesh """
    wavelength: float
    """ Wavelength of the source """
    position: tuple
    """ Position x-y of the source """
    speed_of_light: float = 3e8
    """ Not to be changed """
    amplitude: float = 1.0
    """ Amplitude of the electric field """
    facecolor: str = 'red'
    edgecolor: str = 'red'

    def __post_init__(self):
        self.frequency = self.speed_of_light / self.wavelength

        self.omega = 2 * numpy.pi * self.frequency

        x, y = self.position

        self.p0 = self.grid.get_coordinate(x=x, y=y)

        self.polygon = geo.Point(self.p0.x, self.p0.y)

        self.path = Path(self.polygon.coords)

    def add_to_ax(self, ax: plt.axis) -> NoReturn:
        """
        Add the scatterer to the provided axis as a circle.

        Args:
            ax (Axis): The axis to which the scatterer will be added.
        """
        ax.scatter(
            self.p0.x,
            self.p0.y,
            color=self.facecolor
        )

    def add_source_to_field(self, field: numpy.ndarray, time: float) -> NoReturn:
        rows, cols = self.position
        field[self.p0.x_index, self.p0.y_index] += self.amplitude * numpy.sin(self.omega * time)


@dataclass(config=config_dict)
class LineSource(BaseComponent):
    grid: Grid
    """ The grid of the simulation mesh """
    wavelength: float
    """ Wavelength of the source """
    point_0: Tuple[float | str, float | str]
    """ Position x of the source """
    point_1: Tuple[float | str, float | str]
    """ Position x of the source """
    speed_of_light: float = 3e8
    """ Not to be changed """
    amplitude: float = 1.0
    """ Amplitude of the electric field """
    facecolor: str = 'red'
    edgecolor: str = 'red'

    def __post_init__(self):
        self.frequency = self.speed_of_light / self.wavelength

        self.omega = 2 * numpy.pi * self.frequency

        super().__post_init__()

    def build_object(self) -> NoReturn:

        self.p0 = self.grid.get_coordinate(x=self.point_0[0], y=self.point_0[1])
        self.p1 = self.grid.get_coordinate(x=self.point_1[0], y=self.point_1[1])

        position = bresenham_line(
            x0=self.p0.x_index,
            y0=self.p0.y_index,
            x1=self.p1.x_index,
            y1=self.p1.y_index,
        )

        rows, cols = zip(*position.T)

        self.slice_indexes = rows, cols

        p0 = geo.Point(self.p0.x, self.p0.y)
        p1 = geo.Point(self.p1.x, self.p1.y)

        self.polygon = geo.LineString((p0, p1))
        self.path = Path(numpy.array(self.polygon.coords))

    def add_source_to_field(self, field: numpy.ndarray, time: float) -> NoReturn:
        rows, cols = self.slice_indexes
        field[rows, cols] += self.amplitude * numpy.sin(self.omega * time)


# -
