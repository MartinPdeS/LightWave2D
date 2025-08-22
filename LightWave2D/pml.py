#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from pydantic.dataclasses import dataclass
from TypedUnit import AnyUnit, ureg

from LightWave2D.grid import Grid
from LightWave2D.utils import config_dict


@dataclass(config=config_dict, kw_only=True)
class PML:
    """
    Represents a Perfectly Matched Layer (PML) for absorbing boundary conditions in FDTD simulations.

    Parameters
    ----------
    grid : Grid
        The simulation grid.
    width : str
        Width of the PML region in grid cells, expressed as a percentage (e.g., "10%").
    sigma_max : AnyUnit
        Maximum value of the conductivity profile.
    order : int
        Polynomial order of the conductivity profile.
    """
    grid: Grid
    width: str = "10"
    sigma_max: AnyUnit = 0.045 * ureg.siemens / ureg.meter
    order: int = 3

    def __post_init__(self):
        """
        Initialize the PML regions with appropriate conductivity profiles.
        """
        self.sigma_x = np.zeros((self.grid.n_x, self.grid.n_y))
        self.sigma_y = np.zeros((self.grid.n_x, self.grid.n_y))

        y_mesh, x_mesh = np.meshgrid(self.grid.y_stamp, self.grid.x_stamp)

        opposite_width = float(self.width.strip("%"))
        opposite_width = f"{100 - opposite_width}%"
        self.width_start = self.grid.get_coordinate(x=self.width, y=self.width)
        self.width_stop = self.grid.get_coordinate(x=opposite_width, y=opposite_width)

        bottom_boundary = y_mesh < self.width_start.y
        left_boundary = x_mesh < self.width_start.x

        top_boundary = y_mesh > self.width_stop.y
        right_boundary = x_mesh > self.width_stop.x

        _sigma_max = self.sigma_max.to('siemens/meter').magnitude

        self.sigma_y[bottom_boundary] = _sigma_max * ((self.width_start.y.to('meter').magnitude - y_mesh[bottom_boundary].to('meter').magnitude) / self.width_start.y.to('meter').magnitude) ** self.order
        self.sigma_y[top_boundary] = _sigma_max * ((y_mesh[top_boundary].to('meter').magnitude - self.width_stop.y.to('meter').magnitude) / self.width_start.y.to('meter').magnitude) ** self.order
        self.sigma_x[left_boundary] = _sigma_max * ((self.width_start.x.to('meter').magnitude - x_mesh[left_boundary].to('meter').magnitude) / self.width_start.x.to('meter').magnitude) ** self.order
        self.sigma_x[right_boundary] = _sigma_max * ((x_mesh[right_boundary].to('meter').magnitude - self.width_stop.x.to('meter').magnitude) / self.width_start.x.to('meter').magnitude) ** self.order

        self.sigma_x *= ureg.siemens / ureg.meter
        self.sigma_y *= ureg.siemens / ureg.meter

    def add_to_ax(self, ax: plt.Axes, distance_units: ureg.Quantity = ureg.meter) -> None:
        """
        Add the PML regions to a matplotlib axis.

        Parameters
        ----------
        ax : plt.Axes
            The axis to which the PML regions will be added.
        """
        cmap = np.zeros([256, 4])
        cmap[:, 3] = np.linspace(0, 1, 256)
        cmap = ListedColormap(cmap)

        ax.pcolormesh(
            self.grid.x_stamp.to('meter').magnitude,
            self.grid.y_stamp.to('meter').magnitude,
            self.sigma_y.T.to('siemens/meter').magnitude + self.sigma_x.T.to('siemens/meter').magnitude,
            cmap=cmap,
        )

    def plot(self, unit_size: int = 6) -> None:
        """
        Plot the PML regions.

        Parameters
        ----------
        unit_size : int, optional
            Size of each unit in the plot (default is 6).
        """
        figsize = int(unit_size), int(unit_size * self.grid.size_y / self.grid.size_x)
        figure, ax = plt.subplots(1, 1, figsize=figsize)

        ax.set_title('FDTD Simulation PML Regions')
        ax.set_ylabel(r'y position [$\mu$m]')
        ax.set_xlabel(r'x position [$\mu$m]')
        ax.set_aspect('equal')

        self.add_to_ax(ax)
        plt.show()
