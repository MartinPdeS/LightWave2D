#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from typing import Tuple, NoReturn, Union
from LightWave2D.utils import bresenham_line
from matplotlib.path import Path
import shapely.geometry as geo
import matplotlib.pyplot as plt
from LightWave2D.physics import Physics
from LightWave2D.grid import Grid
from LightWave2D.binary import interface_source
from pydantic.dataclasses import dataclass
from LightWave2D import units


# Configuration dictionary for dataclasses
config_dict = {
    'kw_only': True,
    'extra': 'forbid',
    'slots': True,
    'arbitrary_types_allowed': True
}

class BaseSource():
    """
    Base class for sources in a 2D light wave simulation.
    """
    def plot(self) -> NoReturn:
        """
        Plot the source on a 2D grid.
        """
        figure, ax = plt.subplots(1, 1, figsize=(6, 6))
        ax.set_title('FDTD Simulation')
        ax.set_xlabel(r'x position [m]')
        ax.set_ylabel(r'y position [m]')
        ax.set_aspect('equal')
        self.add_to_ax(ax)
        plt.show()


class MultiWavelength():
    """
    Class for managing multiple wavelengths in a simulation.
    """
    def add_source_to_field(self, field: np.ndarray, time: float) -> NoReturn:
        """
        Add the multi-wavelength source's effect to the simulation field.

        Parameters
        ----------
        field : np.ndarray
            The simulation field to which the source's effect will be added.
        time : float
            The current simulation time.
        """
        rows, cols = self._slc
        field[rows, cols] = self.amplitude * np.sin(self.omega * time)


class Impulsion:
    """
    Represents an impulsion source in the simulation.
    """
    def add_source_to_field(self, field: np.ndarray, time: float) -> NoReturn:
        """
        Add the line impulsion source's effect to the simulation field.

        Parameters
        ----------
        field : np.ndarray
            The simulation field to which the source's effect will be added.
        time : float
            The current simulation time.
        """
        rows, cols = self.slice_indexes
        source_field = np.exp(-((time - self.delay) / self.duration) ** 2)
        field[rows, cols] = self.amplitude * source_field


class Line:
    """
    Represents a line source in the simulation.

    """
    def build_geometry(self) -> NoReturn:
        """
        Build the geometry for the line source and calculate its coordinates.
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
        self._slc = np.atleast_2d(np.c_[rows, cols])

        p0 = geo.Point(self.p0.x.to('meter').magnitude, self.p0.y.to('meter').magnitude)
        p1 = geo.Point(self.p1.x.to('meter').magnitude, self.p1.y.to('meter').magnitude)
        self.polygon = geo.LineString((p0, p1))

    def add_to_ax(self, ax: plt.Axes, distance_units: units.Quantity = units.meter) -> NoReturn:
        """
        Add the line source to the provided axis.

        Parameters
        ----------
        ax : plt.Axes
            The axis to which the line source will be added.
        """
        ax.plot(
            self.polygon.xy[0],
            self.polygon.xy[1],
            color=self.facecolor,
            label='source'
        )

class Point:
    """
    Represents a point source in the simulation.
    """
    def build_geometry(self) -> NoReturn:
        """
        Build the geometry for the point source and calculate its coordinates.
        """
        x, y = self.position
        self.p0 = self.grid.get_coordinate(x=x, y=y)
        self.polygon = geo.Point(self.p0.x.to('meter').magnitude, self.p0.y.to('meter').magnitude)
        self.path = Path(self.polygon.coords)
        self.indexes = np.asarray([[self.p0.x_index, self.p0.y_index]])
        self._slc = np.atleast_2d([[self.p0.x_index, self.p0.y_index]])

    def add_to_ax(self, ax: plt.Axes) -> NoReturn:
        """
        Add the point source to the provided axis as a scatter point.

        Parameters
        ----------
        ax : plt.Axes
            The axis to which the point source will be added.
        """
        ax.scatter(
            self.p0.x.to('meter').magnitude,
            self.p0.y.to('meter').magnitude,
            color=self.facecolor,
            label='source'
        )

@dataclass(config=config_dict)
class PointWaveSource(interface_source.MultiWavelength, MultiWavelength, BaseSource, Point):
    """
    Represents a point source in a 2D light wave simulation.

    Parameters
    ----------
    grid : Grid
        The grid of the simulation mesh.
    wavelength : Union[float, list, np.ndarray]
        Wavelength of the source.
    position : Tuple[Union[float, str], Union[float, str]]
        Position (x, y) of the source.
    amplitude : float
        Amplitude of the electric field.
    edgecolor : str, optional
        Color of the source edge (default is 'red').
    facecolor : str, optional
        Color of the source face (default is 'red').
    alpha : float, optional
        Transparency level of the source (default is 0.3).
    """
    grid: Grid
    wavelength: units.Quantity
    position: Tuple[units.Quantity | str, units.Quantity | str]
    amplitude: float
    edgecolor: str = 'red'
    facecolor: str = 'red'
    alpha: float = 0.3

    def __post_init__(self):
        self.wavelength = np.atleast_1d(self.wavelength)
        self.amplitude = np.atleast_1d(self.amplitude)

        self._slc = None

        if self.wavelength.size != self.amplitude.size:
            raise ValueError('Size of wavelength and amplitude and (option) delay must be the same.')

        self.frequency = Physics.c / self.wavelength
        self.omega = np.atleast_1d(2 * np.pi * self.frequency)

        self.build_geometry()

        super().__init__(
            omega=self.omega.to('hertz').magnitude,
            amplitude=self.amplitude,
            delay=np.zeros(self.amplitude.shape),
            indexes=self._slc
        )

@dataclass(config=config_dict)
class LineWaveSource(interface_source.MultiWavelength, MultiWavelength, BaseSource, Line):
    """
    Represents a line source in a 2D light wave simulation.

    Parameters
    ----------
    grid : Grid
        The grid of the simulation mesh.
    amplitude : float
        Amplitude of the electric field.
    wavelength : units.Quantity
        Wavelength of the source.
    position_0 : Tuple[Union[float, str], Union[float, str]]
        Starting position (x, y) of the source.
    position_1 : Tuple[Union[float, str], Union[float, str]]
        Ending position (x, y) of the source.
    delay : Optional[units.Quantity], optional
        Delay before the source starts (default is None).
    edgecolor : str, optional
        Color of the source edge (default is 'red').
    facecolor : str, optional
        Color of the source face (default is 'red').
    alpha : float, optional
        Transparency level of the source (default is 0.3).
    """
    grid: Grid
    amplitude: float
    wavelength: units.Quantity
    position_0: Tuple[units.Quantity | str, units.Quantity | str]
    position_1: Tuple[units.Quantity | str, units.Quantity | str]
    edgecolor: str = 'red'
    facecolor: str = 'red'
    alpha: float = 0.3

    def __post_init__(self):
        self.wavelength = np.atleast_1d(self.wavelength)
        self.amplitude = np.atleast_1d(self.amplitude)

        self._slc = None

        if self.wavelength.size != self.amplitude.size:
            raise ValueError('Size of wavelength and amplitude and (option) delay must be the same.')

        self.frequency = Physics.c / self.wavelength
        self.omega = np.atleast_1d(2 * np.pi * self.frequency)

        self.build_geometry()

        super().__init__(
            omega=self.omega.to('hertz').magnitude,
            amplitude=self.amplitude,
            delay=np.zeros(self.amplitude.shape),
            indexes=self._slc
        )


@dataclass(config=config_dict)
class PointPulseSource(Impulsion, Point, BaseSource):
    """
    Represents a point impulsion source in a 2D light wave simulation.

    Parameters
    ----------
    grid : Grid
        The grid of the simulation mesh.
    amplitude : float
        Amplitude of the electric field.
    duration : units.Quantity
        Duration of the impulsion.
    position : Tuple[Union[float, str], Union[float, str]]
        Position (x, y) of the source.
    delay : units.Quantity, optional
        Delay before the impulsion starts (default is 0 seconds).
    edgecolor : str, optional
        Color of the source edge (default is 'red').
    facecolor : str, optional
        Color of the source face (default is 'red').
    alpha : float, optional
        Transparency level of the source (default is 0.3).
    """
    grid: Grid
    amplitude: float
    duration: units.Quantity
    position: Tuple[units.Quantity | str, units.Quantity | str]
    delay: units.Quantity = 0 * units.second
    edgecolor: str = 'red'
    facecolor: str = 'red'
    alpha: float = 0.3

    def __post_init__(self):
        self._slc = None

        self.build_geometry()

        super().__init__(
            amplitude=self.amplitude,
            duration=self.duration.to('second').magnitude,
            delay=self.delay.to('second').magnitude,
            indexes=self._slc
        )

@dataclass(config=config_dict)
class LinePulseSource(interface_source.Impulsion, Impulsion, Line, BaseSource):
    """
    Represents a line pulse source in a 2D light wave simulation.

    Parameters
    ----------
    grid : Grid
        The grid of the simulation mesh.
    duration : units.Quantity
        Duration of the impulsion.
    amplitude : float
        Amplitude of the electric field.
    position_0 : Tuple[Union[float, str], Union[float, str]]
        Starting position (x, y) of the source.
    position_1 : Tuple[Union[float, str], Union[float, str]]
        Ending position (x, y) of the source.
    delay : units.Quantity, optional
        Delay before the impulsion starts (default is 0 seconds).
    edgecolor : str, optional
        Color of the source edge (default is 'red').
    facecolor : str, optional
        Color of the source face (default is 'red').
    alpha : float, optional
        Transparency level of the source (default is 0.3).
    """
    grid: Grid
    duration: units.Quantity
    amplitude: float
    position_0: Tuple[units.Quantity | str, units.Quantity | str]
    position_1: Tuple[units.Quantity | str, units.Quantity | str]
    delay: units.Quantity = 0 * units.second
    edgecolor: str = 'red'
    facecolor: str = 'red'
    alpha: float = 0.3

    def __post_init__(self):
        self._slc = None

        self.build_geometry()

        super().__init__(
            amplitude=self.amplitude,
            duration=self.duration.to('second').magnitude,
            delay=self.delay.to('second').magnitude,
            indexes=self._slc
        )
