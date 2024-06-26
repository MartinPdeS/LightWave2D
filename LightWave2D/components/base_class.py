#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import NoReturn

import numpy
from LightWave2D.physics import Physics
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch


class BaseComponent():
    def __post_init__(self):
        self.build_object()

    def build_object(self) -> NoReturn:
        """
        Build the permittivity mesh for the square scatterer.
        """
        self.epsilon_r_mesh = numpy.ones(self.grid.shape)  # Background permittivity

        self.compute_path()

        x_mesh, y_mesh = numpy.meshgrid(self.grid.x_stamp, self.grid.y_stamp)

        coordinates = numpy.c_[x_mesh.T.flatten(), y_mesh.T.flatten()]

        self.idx = self.path.contains_points(coordinates).astype(bool).reshape(self.epsilon_r_mesh.shape)

        self.epsilon_r_mesh[self.idx] = self.epsilon_r

    def add_to_ax(self, ax: plt.axis) -> NoReturn:
        """
        Add the scatterer to the provided axis as a circle.

        Args:
            ax (Axis): The axis to which the scatterer will be added.
        """
        patch = PathPatch(
            self.path,
            alpha=0.7,
            color=self.facecolor,
            label=str(self.__class__.__name__),
        )

        return ax.add_patch(patch)

    def plot(self) -> NoReturn:
        figure, ax = plt.subplots(1, 1, figsize=(6, 6))
        ax.set_title('FDTD Simulation')
        ax.set_xlabel(r'x position [$\mu$m]')
        ax.set_xlabel(r'y position [$\mu$m]')
        ax.set_aspect('equal')

        self.add_to_ax(ax)
        ax.autoscale_view()

        plt.show()

    def interpret_position_to_index(self) -> tuple:
        """
        Interprets and returns the value of positions x and y of the waveguide

        :returns:   The index of width and height
        :rtype:     int
        """
        x, y = self.position

        if isinstance(x, str):
            x_index = self.grid.string_to_index(x, axis='x')
        else:
            x_index = self.grid.position_to_index(x, axis='x')

        if isinstance(y, str):
            y_index = self.grid.string_to_index(y, axis='y')
        else:
            y_index = self.grid.position_to_index(y, axis='y')

        return x_index, y_index

    def interpret_position_to_position(self) -> tuple:
        """
        Interprets and returns the value of positions x and y of the waveguide

        :returns:   The index of width and height
        :rtype:     int
        """
        x, y = self.position

        coordinate = self.grid.get_coordinate(x=x, y=y)

        return coordinate.x, coordinate.y

    def add_to_mesh(self, epsilon_r_mesh: numpy.ndarray) -> None:
        epsilon_r_mesh += self.epsilon_r_mesh

    def add_non_linear_effect_to_field(self, field: numpy.ndarray) -> None:
        chi_2 = 1e10

        field += self.idx * self.grid.dt**2 / (self.epsilon_r_mesh * Physics.epsilon_0 * Physics.mu_0) * chi_2 * field ** 2
