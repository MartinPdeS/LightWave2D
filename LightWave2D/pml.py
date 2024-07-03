#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import NoReturn
import numpy as np
import numpy
from LightWave2D.grid import Grid
from pydantic.dataclasses import dataclass
from matplotlib.colors import ListedColormap
import matplotlib.pyplot as plt

# Configuration dictionary for dataclasses
config_dict = {
    'kw_only': True,
    'slots': True,
    'extra': 'forbid',
    'arbitrary_types_allowed': True
}


@dataclass(config=config_dict)
class PML:
    """
    Represents a Perfectly Matched Layer (PML) for absorbing boundary conditions in FDTD simulations.

    Attributes:
        grid (Grid): The simulation grid.
        width (int): Width of the PML region in grid cells.
        sigma_max (float): Maximum value of the conductivity profile.
        order (int): Polynomial order of the conductivity profile.
    """
    grid: Grid
    width: str = 10
    sigma_max: float = 0.045
    order: int = 3

    def __post_init__(self):
        """
        Initialize the PML regions with appropriate conductivity profiles.
        """
        self.sigma_x = np.zeros((self.grid.n_x, self.grid.n_y))
        self.sigma_y = np.zeros((self.grid.n_x, self.grid.n_y))

        y_mesh, x_mesh = numpy.meshgrid(self.grid.y_stamp, self.grid.x_stamp)

        opposite_width = float(self.width.strip("%"))
        opposite_width = f"{100 - opposite_width}%"
        self.width_start = self.grid.get_coordinate(x=self.width, y=self.width)
        self.width_stop = self.grid.get_coordinate(x=opposite_width, y=opposite_width)

        bottom_boundary = y_mesh < self.width_start.y
        left_boundary = x_mesh < self.width_start.x

        top_boundary = y_mesh > self.width_stop.y
        right_boundary = x_mesh > self.width_stop.x

        self.sigma_y[bottom_boundary] = self.sigma_max * ((self.width_start.y - y_mesh[bottom_boundary]) / self.width_start.y) ** self.order
        self.sigma_y[top_boundary] = self.sigma_max * ((y_mesh[top_boundary] - self.width_stop.y) / self.width_start.y) ** self.order
        self.sigma_x[left_boundary] = self.sigma_max * ((self.width_start.x - x_mesh[left_boundary]) / self.width_start.x) ** self.order
        self.sigma_x[right_boundary] = self.sigma_max * ((x_mesh[right_boundary] - self.width_stop.x) / self.width_start.x) ** self.order

    def add_to_ax(self, ax: plt.Axes) -> NoReturn:
        """
        Add the PML regions to a matplotlib axis.

        Args:
            ax (plt.Axes): The axis to which the PML regions will be added.
        """
        cmap = np.zeros([256, 4])
        cmap[:, 3] = np.linspace(0, 1, 256)
        cmap = ListedColormap(cmap)

        ax.pcolormesh(
            self.grid.x_stamp,
            self.grid.y_stamp,
            self.sigma_y.T + self.sigma_x.T,
            cmap=cmap,
        )

    def plot(self, unit_size: int = 6) -> NoReturn:
        """
        Plot the PML regions.

        Args:
            unit_size (int): Size of each unit in the plot.
        """
        figsize = int(unit_size), int(unit_size * self.grid.size_y / self.grid.size_x)
        figure, ax = plt.subplots(1, 1, figsize=figsize)

        ax.set_title('FDTD Simulation PML Regions')
        ax.set_ylabel(r'y position [$\mu$m]')
        ax.set_xlabel(r'x position [$\mu$m]')
        ax.set_aspect('equal')

        self.add_to_ax(ax)
        plt.show()
