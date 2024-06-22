#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Tuple
import numpy
from MPSPlots.render2D import SceneList, Axis
from LightWave2D.grid import Grid
from LightWave2D.utils import bresenham_line
from pydantic.dataclasses import dataclass

config_dict = dict(
    kw_only=True,
    slots=True,
    extra='forbid',
    arbitrary_types_allowed=True
)


@dataclass(config=config_dict)
class PointSource():
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

    def __post_init__(self):
        self.frequency = self.speed_of_light / self.wavelength

        self.omega = 2 * numpy.pi * self.frequency

        x, y = self.position

        self.p0 = self.grid.get_coordinate(x=x, y=y)

    def add_source_to_field(self, field: numpy.ndarray, time) -> None:
        rows, cols = self.slice_indexes
        field[self.p0.x_index, self.p0.y_index] += self.amplitude * numpy.sin(self.omega * time)


@dataclass(config=config_dict)
class LineSource():
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

    def __post_init__(self):
        self.frequency = self.speed_of_light / self.wavelength

        self.omega = 2 * numpy.pi * self.frequency

        self.build_line()

    def build_line(self) -> None:

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

    def add_source_to_field(self, field: numpy.ndarray, time) -> None:
        rows, cols = self.slice_indexes
        field[rows, cols] += self.amplitude * numpy.sin(self.omega * time)

    def add_to_ax(self, ax: Axis) -> None:
        ax.add_line(
            x=[self.p0.x, self.p1.x],
            y=[self.p0.y, self.p1.y],
            color='red',
            line_width=2,
            label='source'
        )

    def plot(self) -> SceneList:
        scene = SceneList(
            unit_size=(4, 4),
            title='FDTD Simulation at time step'
        )

        ax = scene.append_ax(
            x_label=r'x position [$\mu$m]',
            y_label=r'y position [$\mu$m]',
            aspect_ratio='equal',
            equal_limits=True
        )

        self.add_to_ax(ax)

        ax.add_colorbar(colormap='Blues')

        return scene

# -
