#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import NoReturn
import numpy
from LightWave2D.grid import Grid
from pydantic.dataclasses import dataclass
from matplotlib.colors import ListedColormap
import matplotlib.pyplot as plt

config_dict = dict(
    kw_only=True,
    slots=True,
    extra='forbid',
    arbitrary_types_allowed=True
)


@dataclass(config=config_dict)
class PML():
    grid: Grid
    """ The grid of the simulation mesh """
    width: int = 10
    """ Width of the PML region """
    sigma_max: float = 0.045
    """ Adjust sigma_max for better absorption, based on wavelength and PML width """
    order: int = 3
    """ Polynomial order of sigma profile """

    def __post_init__(self):
        self.sigma_x = numpy.zeros((self.grid.n_x, self.grid.n_y))
        self.sigma_y = numpy.zeros((self.grid.n_x, self.grid.n_y))

        for i in range(self.grid.n_x):
            for j in range(self.grid.n_y):
                # Left and right PML regions
                if i < self.width:
                    self.sigma_x[i, j] = self.sigma_max * ((self.width - i) / self.width) ** self.order
                elif i >= self.grid.n_x - self.width:
                    self.sigma_x[i, j] = self.sigma_max * ((i - (self.grid.n_x - self.width - 1)) / self.width) ** self.order

                # Top and bottom PML regions
                if j < self.width:
                    self.sigma_y[i, j] = self.sigma_max * ((self.width - j) / self.width) ** self.order
                elif j >= self.grid.n_y - self.width:
                    self.sigma_y[i, j] = self.sigma_max * ((j - (self.grid.n_y - self.width - 1)) / self.width) ** self.order

    def add_to_ax(self, ax: plt.axis) -> NoReturn:
        cmap = numpy.zeros([256, 4])
        cmap[:, 3] = numpy.linspace(0, 1, 256)
        cmap = ListedColormap(cmap)

        ax.pcolormesh(
            self.grid.x_stamp,
            self.grid.y_stamp,
            self.sigma_y.T + self.sigma_x.T,
            cmap=cmap,
        )

    def plot(self, unit_size: int = 6) -> NoReturn:
        figsize = int(unit_size), int(unit_size * self.grid.size_y / self.grid.size_x)
        figure, ax = plt.subplots(1, 1, figsize=figsize)

        ax.set_title('FDTD Simulation at time step')
        ax.set_ylabel(r'y position [$\mu$m]')
        ax.set_xlabel(r'x position [$\mu$m]')
        ax.set_aspect('equal')

        self.add_to_ax(ax)

        plt.show()

# -
