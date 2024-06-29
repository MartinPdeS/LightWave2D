#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import NoReturn
from pydantic.dataclasses import dataclass
import numpy
from LightWave2D.physics import Physics
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch
import matplotlib as mpl
import numpy as np
from matplotlib.path import Path
from matplotlib.collections import PatchCollection


# Configuration dictionary for dataclasses
config_dict = {
    'kw_only': True,
    'extra': 'forbid',
    'slots': True,
    'arbitrary_types_allowed': True
}


@dataclass(kw_only=True, config=config_dict)
class BaseComponent():
    """
    Represents an elliptical scatterer in a simulation grid.

    Attributes:
        grid (Grid): The grid of the simulation mesh.
        angle (float): Rotation angle of the ellipse.
        facecolor (str): Color of the scatterer face.
        edgecolor (str): Color of the scatterer edge.
    """
    facecolor: str = 'lightblue'
    edgecolor: str = 'blue'
    alpha: float = 0.3
    rotation: float = 0

    def __post_init__(self):
        x0, y0 = self.position
        self.coordinate = self.grid.get_coordinate(x=x0, y=y0)

        self.build_object()

    def build_object(self) -> NoReturn:
        """
        Build the permittivity mesh for the square scatterer.
        """
        self.epsilon_r_mesh = numpy.ones(self.grid.shape)  # Background permittivity

        self.compute_polygon()

        self.path = Path(self.polygon.exterior.coords)

        self.path = self.path.transformed(mpl.transforms.Affine2D().rotate_around(self.coordinate.x, self.coordinate.y, self.rotation))

        x_mesh, y_mesh = numpy.meshgrid(self.grid.x_stamp, self.grid.y_stamp)

        coordinates = numpy.c_[x_mesh.T.flatten(), y_mesh.T.flatten()]

        self.idx = self.path.contains_points(coordinates).astype(bool).reshape(self.epsilon_r_mesh.shape)

        self.epsilon_r_mesh[self.idx] = self.epsilon_r

    def add_to_ax(self, ax: plt.axis) -> PatchCollection:
        """
        Add the scatterer to the provided axis as a circle.

        Args:
            ax (Axis): The axis to which the scatterer will be added.
        """
        path = Path.make_compound_path(
            Path(np.asarray(self.polygon.exterior.coords)[:, :2]),
            *[Path(np.asarray(ring.coords)[:, :2]) for ring in self.polygon.interiors])

        patch = PathPatch(path, color=self.facecolor, edgecolor=self.edgecolor, alpha=0.4)
        collection = PatchCollection([patch], color=self.facecolor, edgecolor=self.edgecolor, alpha=self.alpha)

        ax.add_collection(collection, autolim=True)
        ax.autoscale_view()
        return collection

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
