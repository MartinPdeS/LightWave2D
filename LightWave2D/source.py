#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from typing import Tuple, NoReturn, List, Union, Optional
from LightWave2D.utils import bresenham_line
from pydantic.dataclasses import dataclass
from matplotlib.path import Path
import shapely.geometry as geo
import matplotlib.pyplot as plt
from LightWave2D.physics import Physics
from LightWave2D.grid import Grid
from LightWave2D.binary import SourceInterface

# Configuration dictionary for dataclasses
config_dict = {
    'kw_only': True,
    'extra': 'forbid',
    'slots': True,
    'arbitrary_types_allowed': True
}


@dataclass(kw_only=True, config=config_dict)
class BaseSource:
    """
    Base class for sources in a 2D light wave simulation.

    Parameters
    ----------
    grid : Grid
        The grid of the simulation mesh.
    facecolor : str, optional
        Color of the source face (default is 'red').
    edgecolor : str, optional
        Color of the source edge (default is 'red').
    alpha : float, optional
        Transparency level of the source (default is 0.3).
    """
    grid: Grid
    facecolor: str = 'red'
    edgecolor: str = 'red'
    alpha: float = 0.3

    def plot(self) -> NoReturn:
        """
        Plot the source on a 2D grid.
        """
        figure, ax = plt.subplots(1, 1, figsize=(6, 6))
        ax.set_title('FDTD Simulation')
        ax.set_xlabel(r'x position [$\mu$m]')
        ax.set_ylabel(r'y position [$\mu$m]')
        ax.set_aspect('equal')
        self.add_to_ax(ax)
        plt.show()


@dataclass(config=config_dict)
class MultiWavelenth:
    """
    Class for managing multiple wavelengths in a simulation.

    Parameters
    ----------
    wavelength : Union[float, List[float], np.ndarray]
        Wavelength(s) of the source.
    amplitude : Union[float, List[float], np.ndarray]
        Amplitude(s) of the source.
    delay : Optional[Union[float, List[float], np.ndarray]], optional
        Delay(s) for each wavelength (default is None).
    """
    wavelength: Union[float, List[float], np.ndarray]
    amplitude: Union[float, List[float], np.ndarray]
    delay: Optional[Union[float, List[float], np.ndarray]] = None

    def init_base_parameters(self) -> NoReturn:
        """
        Initialize the base parameters for the wavelengths.
        """
        self.wavelength = np.atleast_1d(self.wavelength)
        self.amplitude = np.atleast_1d(self.amplitude)

        if self.wavelength.size != self.amplitude.size:
            raise ValueError('Size of wavelength and amplitude and (option) delay must be the same.')

        if not self.delay:
            self.delay = np.zeros(self.wavelength.size)

        self.delay = np.atleast_1d(self.delay)

        self.frequency = Physics.c / self.wavelength
        self.omega = np.atleast_1d(2 * np.pi * self.frequency)

    def build_object(self) -> NoReturn:
        """
        Build the multi-wavelength source object and calculate its coordinates.
        """
        self.binding = SourceInterface.MultiWavelength(
            omega=self.omega,
            amplitude=self.amplitude,
            delay=np.zeros(self.amplitude.shape),
            indexes=self._slc
        )

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


@dataclass(config=config_dict)
class Impulsion:
    """
    Represents an impulsion source in the simulation.

    Parameters
    ----------
    amplitude : float
        Amplitude of the impulsion.
    duration : float
        Duration of the impulsion.
    delay : float
        Delay before the impulsion starts.
    """
    amplitude: float
    duration: float
    delay: float

    def init_base_parameters(self) -> NoReturn:
        """Initialize base parameters (if needed)."""
        pass

    def build_object(self) -> NoReturn:
        """
        Build the impulsion source object and calculate its coordinates.
        """
        self.binding = SourceInterface.Impulsion(
            amplitude=self.amplitude,
            duration=self.duration,
            delay=self.delay,
            indexes=self._slc
        )

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


@dataclass(config=config_dict)
class Line:
    """
    Represents a line source in the simulation.

    Parameters
    ----------
    position_0 : Tuple[Union[float, str], Union[float, str]]
        Starting position of the line.
    position_1 : Tuple[Union[float, str], Union[float, str]]
        Ending position of the line.
    """
    position_0: Tuple[Union[float, str], Union[float, str]]
    position_1: Tuple[Union[float, str], Union[float, str]]

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

        p0 = geo.Point(self.p0.x, self.p0.y)
        p1 = geo.Point(self.p1.x, self.p1.y)
        self.polygon = geo.LineString((p0, p1))

    def add_to_ax(self, ax: plt.Axes) -> NoReturn:
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


@dataclass(config=config_dict)
class Point:
    """
    Represents a point source in the simulation.

    Parameters
    ----------
    position : Tuple[Union[float, str], Union[float, str]]
        Position (x, y) of the point in the simulation grid.
    """
    position: Tuple[Union[float, str], Union[float, str]]

    def build_geometry(self) -> NoReturn:
        """
        Build the geometry for the point source and calculate its coordinates.
        """
        x, y = self.position
        self.p0 = self.grid.get_coordinate(x=x, y=y)
        self.polygon = geo.Point(self.p0.x, self.p0.y)
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
            self.p0.x,
            self.p0.y,
            color=self.facecolor,
            label='source'
        )


@dataclass(config=config_dict)
class PointSource(MultiWavelenth, BaseSource, Point):
    """
    Represents a point source in a 2D light wave simulation.

    Parameters
    ----------
    wavelength : Union[float, List[float], np.ndarray]
        Wavelength of the source.
    position : Tuple[Union[float, str], Union[float, str]]
        Position (x, y) of the source.
    amplitude : float
        Amplitude of the electric field.
    """
    position: Tuple[Union[float, str], Union[float, str]]

    def __post_init__(self):
        """
        Post-initialization to set up the base parameters, geometry, and object for the point source.
        """
        self.init_base_parameters()
        self.build_geometry()
        self.build_object()


@dataclass(config=config_dict)
class LineSource(MultiWavelenth, BaseSource, Line):
    """
    Represents a line source in a 2D light wave simulation.

    Parameters
    ----------
    amplitude : float
        Amplitude of the electric field.
    wavelength : float
        Wavelength of the source.
    position_0 : Tuple[Union[float, str], Union[float, str]]
        Starting position (x, y) of the source.
    position_1 : Tuple[Union[float, str], Union[float, str]]
        Ending position (x, y) of the source.
    """

    def __post_init__(self):
        """
        Post-initialization to set up the base parameters, geometry, and object for the line source.
        """
        self.init_base_parameters()
        self.build_geometry()
        self.build_object()


@dataclass(config=config_dict)
class PointImpulsion(Impulsion, Point, BaseSource):
    """
    Represents a point impulsion source in a 2D light wave simulation.

    Parameters
    ----------
    amplitude : float
        Amplitude of the electric field.
    duration : float
        Duration of the impulsion.
    position : Tuple[Union[float, str], Union[float, str]]
        Position (x, y) of the source.
    delay : float
        Delay before the impulsion starts.
    """

    def __post_init__(self):
        """
        Post-initialization to set up the base parameters, geometry, and object for the point impulsion.
        """
        self.init_base_parameters()
        self.build_geometry()
        self.build_object()


@dataclass(config=config_dict)
class LineImpulsion(Impulsion, Line, BaseSource):
    """
    Represents a line impulsion source in a 2D light wave simulation.

    Parameters
    ----------
    duration : float
        Duration of the impulsion.
    amplitude : float
        Amplitude of the electric field.
    position_0 : Tuple[Union[float, str], Union[float, str]]
        Starting position (x, y) of the source.
    position_1 : Tuple[Union[float, str], Union[float, str]]
        Ending position (x, y) of the source.
    delay : float
        Delay before the impulsion starts.
    """

    def __post_init__(self):
        """
        Post-initialization to set up the base parameters, geometry, and object for the line impulsion.
        """
        self.init_base_parameters()
        self.build_geometry()
        self.build_object()
