#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Union, Optional
import numpy
from pydantic.dataclasses import dataclass
import shapely.geometry as geo
from TypedUnit import Length

from LightWave2D.physics import Physics
from LightWave2D.utils import config_dict


class NameSpace:
    """
    A class to dynamically create attributes from keyword arguments.
    """

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


@dataclass(config=config_dict, kw_only=True)
class Grid:
    """
    Represents a 2D simulation grid with specified dimensions and time steps.

    Attributes
    ----------
    resolution : Length
        The spatial resolution of the grid.
    size_x : Length
        The size of the grid in the x-direction.
    size_y : Length
        The size of the grid in the y-direction.
    n_steps : int
        The number of time steps for the simulation (default is 200).
    """
    resolution: Length
    size_x: Length
    size_y: Length
    n_steps: int = 200

    def __post_init__(self):
        self.resolution = self.resolution
        self.size_x = self.size_x
        self.size_y = self.size_y

        self.n_x = int(self.size_x / self.resolution)
        self.n_y = int(self.size_y / self.resolution)
        self.dx = self.size_x / self.n_x  # Should be approximately equal to the resolution
        self.dy = self.size_y / self.n_y  # Should be approximately equal to the resolution
        self.dt = 1 / (Physics.c * numpy.sqrt(1 / self.dx**2 + 1 / self.dy**2))  # Time step size using Courant condition

        self.shape = (self.n_x, self.n_y)
        self.time_stamp = numpy.arange(self.n_steps) * self.dt.to('second')
        self.x_stamp = numpy.linspace(0, self.size_x, self.n_x)
        self.y_stamp = numpy.linspace(0, self.size_y, self.n_y)

        self.x_mesh, self.y_mesh = numpy.meshgrid(self.x_stamp, self.y_stamp)

        self.polygon = geo.Polygon([
            (self.x_stamp[0].to('meter').magnitude, self.y_stamp[0].to('meter').magnitude),
            (self.x_stamp[0].to('meter').magnitude, self.y_stamp[-1].to('meter').magnitude),
            (self.x_stamp[-1].to('meter').magnitude, self.y_stamp[0].to('meter').magnitude),
            (self.x_stamp[-1].to('meter').magnitude, self.y_stamp[-1].to('meter').magnitude)
        ]).convex_hull

    def get_distance_grid(self, x0: float = 0, y0: float = 0) -> numpy.ndarray:
        """
        Compute the distance grid from a given point (x0, y0).

        Args:
            x0 (float): x-coordinate of the reference point (default is 0).
            y0 (float): y-coordinate of the reference point (default is 0).

        Returns:
            numpy.ndarray: A 2D array of distances from the reference point.
        """
        x_mesh, y_mesh = numpy.meshgrid(self.x_stamp, self.y_stamp)
        distance_mesh = numpy.sqrt((x_mesh - x0)**2 + (y_mesh - y0)**2)
        return distance_mesh

    def get_coordinate(self, x: Optional[Union[float, str, Length]] = None, y: Optional[Union[float, str, Length]] = None) -> NameSpace:
        """
        Get the coordinate and index for a given position in the grid.

        Parameters
        ----------
        x : float | str | Length
            The x-coordinate or position string ('left', 'center', 'right').
        y : float | str | Length
            The y-coordinate or position string ('bottom', 'center', 'top').

        Returns
        -------
        NameSpace
            An object containing the coordinates and indices.
        """
        coordinate = NameSpace()

        if isinstance(x, str):
            x = self.parse_x_position(x)
        if isinstance(y, str):
            y = self.parse_y_position(y)

        if x is not None:
            x = numpy.clip(x, self.x_stamp[0], self.x_stamp[-1])
            coordinate.x = x
            coordinate.x_index = int(x / self.dx)

        if y is not None:
            y = numpy.clip(y, self.y_stamp[0], self.y_stamp[-1])
            coordinate.y = y
            coordinate.y_index = int(y / self.dy)

        return coordinate

    def parse_y_position(self, value: Union[str, float, Length]) -> float:
        """
        Convert a position string to a y-coordinate.

        Parameters
        ----------
        value : str | float | Length
            The position string or coordinate value.

        Returns
        -------
        float
            The corresponding y-coordinate.
        """
        if isinstance(value, str):
            value = value.lower()
            if '%' in value:
                percentage = float(value.strip('%')) / 100.0
                delta = self.y_stamp[-1] - self.y_stamp[0]

                return self.y_stamp[0] + percentage * delta

            assert value in ['bottom', 'center', 'top'], f"Invalid position: {value}. Valid inputs are ['bottom', 'center', 'top']."
            match value:
                case 'bottom':
                    return self.y_stamp[0]
                case 'center':
                    return numpy.mean(self.y_stamp)
                case 'top':
                    return self.y_stamp[-1]

        return value

    def parse_x_position(self, value: Union[str, float, Length]) -> float:
        """
        Convert a position string to an x-coordinate.

        Parameters
        ----------
        value : str | float | Length
            The position string or coordinate value.

        Returns
        -------
        float
            The corresponding x-coordinate.
        """
        if isinstance(value, str):
            value = value.lower()
            if '%' in value:
                percentage = float(value.strip('%')) / 100.0
                delta = self.x_stamp[-1] - self.x_stamp[0]

                return self.x_stamp[0] + percentage * delta

            assert value in ['right', 'center', 'left'], f"Invalid position: {value}. Valid inputs are ['right', 'center', 'left']."
            match value:
                case 'right':
                    return self.x_stamp[-1]
                case 'center':
                    return numpy.mean(self.x_stamp)
                case 'left':
                    return self.x_stamp[0]

        return value
