#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Tuple, Union, NoReturn
from pydantic.dataclasses import dataclass
from LightWave2D.grid import Grid
from LightWave2D.components.base_class import BaseComponent
from matplotlib.path import Path
import shapely.geometry as geo

# Configuration dictionary for dataclasses
config_dict = {
    'kw_only': True,
    'extra': 'forbid',
    'slots': True,
    'arbitrary_types_allowed': True
}


@dataclass(config=config_dict)
class Grating(BaseComponent):
    """
    Represents a grating in a simulation grid.

    Attributes:
        position (Tuple[Union[float, str], Union[float, str]]): Starting position of the grating.
        epsilon_r (float): Relative permittivity inside the grating.
        period (float): Period of the grating.
        duty_cycle (float): Duty cycle of the grating (fraction of period occupied by the grating material).
        num_periods (int): Number of grating periods.
    """
    position: Tuple[Union[float, str], Union[float, str]]
    epsilon_r: float
    period: float
    duty_cycle: float
    num_periods: int

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


@dataclass(config=config_dict)
class RingResonator(BaseComponent):
    """
    Represents a ring resonator in a simulation grid.

    Attributes:
        position (Tuple[Union[float, str], Union[float, str]]): Starting position of the resonator (center of the ring).
        epsilon_r (float): Relative permittivity inside the resonator.
        inner_radius (float): Inner radius of the ring.
        width (float): Outer radius of the ring.
    """
    grid: Grid
    position: Tuple[Union[float, str], Union[float, str]]
    epsilon_r: float
    inner_radius: float
    width: float

    def compute_polygon(self) -> Path:
        """
        Compute the path of the ring resonator.
        """
        inner_circle = geo.Point(self.coordinate.x, self.coordinate.y).buffer(self.inner_radius)
        outer_circle = geo.Point(self.coordinate.x, self.coordinate.y).buffer(self.inner_radius + self.width)
        self.polygon = outer_circle.difference(inner_circle)


@dataclass(config=config_dict)
class Lense(BaseComponent):
    """
    Represents a lens in a simulation grid.

    Attributes:
        position (Tuple[Union[float, str], Union[float, str]]): Starting position of the lens (center of the lens).
        epsilon_r (float): Relative permittivity inside the lens.
        radius (float): Radius of the lens.
        curvature (float): Curvature of the lens (positive for convex, negative for concave).
    """
    position: Tuple[Union[float, str], Union[float, str]]
    epsilon_r: float
    width: float
    curvature: float

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
