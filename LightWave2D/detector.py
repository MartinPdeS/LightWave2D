#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Tuple, Union, NoReturn
from dataclasses import field
import numpy as np
from LightWave2D.grid import Grid
import shapely.geometry as geo
from matplotlib.path import Path
from pydantic.dataclasses import dataclass
from matplotlib.collections import PatchCollection
from matplotlib.patches import PathPatch
import matplotlib.pyplot as plt
import matplotlib

config_dict = dict(
    kw_only=True,
    slots=True,
    extra='forbid',
    arbitrary_types_allowed=True
)


@dataclass(kw_only=True, config=config_dict)
class BaseDetector:
    """
    Base class representing a scatterer (detector) in a simulation grid.

    Attributes
    ----------
    grid : Grid
        The grid of the simulation mesh.
    facecolor : str, optional
        Color of the scatterer face (default is 'green').
    edgecolor : str, optional
        Color of the scatterer edge (default is 'green').
    alpha : float, optional
        Transparency level of the scatterer (default is 0.8).
    rotation : float, optional
        Rotation angle of the scatterer (default is 0 degrees).
    """
    grid: Grid
    facecolor: str = 'green'
    edgecolor: str = 'green'
    alpha: float = 0.8
    rotation: float = 0

    def __post_init__(self):
        """
        Initialize the scatterer by building its object and computing the coordinate.
        """
        x0, y0 = self.position
        self.coordinate = self.grid.get_coordinate(x=x0, y=y0)
        self.build_object()

    def build_object(self) -> NoReturn:
        """
        Build the permittivity mesh for the scatterer.
        """
        self.compute_polygon()
        self.path = Path(self.polygon.exterior.coords)
        self.path = self.path.transformed(
            matplotlib.transforms.Affine2D().rotate_around(self.coordinate.x, self.coordinate.y, self.rotation)
        )

    def add_to_ax(self, ax: plt.Axes) -> PatchCollection:
        """
        Add the scatterer to the provided axis.

        Parameters
        ----------
        ax : plt.Axes
            The axis to which the scatterer will be added.

        Returns
        -------
        PatchCollection
            A collection of patches representing the scatterer.
        """
        path = Path.make_compound_path(
            Path(np.asarray(self.polygon.exterior.coords)[:, :2]),
            *[Path(np.asarray(ring.coords)[:, :2]) for ring in self.polygon.interiors]
        )

        patch = PathPatch(path, color=self.facecolor, edgecolor=self.edgecolor, alpha=0.4)
        collection = PatchCollection([patch], color=self.facecolor, edgecolor=self.edgecolor, alpha=self.alpha)

        ax.add_collection(collection, autolim=True)
        ax.autoscale_view()
        return collection

    def plot(self) -> NoReturn:
        """
        Plot the scatterer on a 2D grid.
        """
        figure, ax = plt.subplots(1, 1, figsize=(6, 6))
        ax.set_title('FDTD Simulation')
        ax.set_xlabel(r'x position [$\mu$m]')
        ax.set_ylabel(r'y position [$\mu$m]')
        ax.set_aspect('equal')

        self.add_to_ax(ax)
        ax.autoscale_view()

        plt.show()


@dataclass(kw_only=True, config=config_dict)
class PointDetector(BaseDetector):
    """
    Represents a point detector within a simulation grid.

    Attributes
    ----------
    grid : Grid
        The simulation mesh grid.
    position : Tuple[Union[float, str], Union[float, str]]
        The (x, y) coordinates of the point detector on the grid.
    coherent : bool, optional
        Whether the detector collects coherent data (default is True).
    data : numpy.ndarray
        The data collected by the detector over time.
    """
    position: Union[Tuple[float, str], Tuple[str, str]]
    coherent: bool = True
    data: np.ndarray = field(init=False)

    def __post_init__(self):
        """
        Initialize the PointDetector by converting the given position into
        grid coordinates and initializing the data array.
        """
        x, y = self.position
        self.p0 = self.grid.get_coordinate(x=x, y=y)
        self.polygon = geo.Point(self.p0.x, self.p0.y)
        self.path = Path(self.polygon.coords)
        self.data = np.zeros(self.grid.n_steps)

    def update_data(self, field: np.ndarray) -> NoReturn:
        """
        Update the detector data based on the provided field values.

        Parameters
        ----------
        field : numpy.ndarray
            The field values to update the detector data.
        """
        if self.coherent:
            self.data = field[:, self.p0.x_index, self.p0.y_index]
        else:
            self.data = abs(field[:, self.p0.x_index, self.p0.y_index])

    def plot_data(self) -> NoReturn:
        """
        Plot the detector data over time.
        """
        figure, ax = plt.subplots(1, 1, figsize=(8, 4))
        ax.plot(self.grid.time_stamp, self.data)
        ax.set_ylabel('Amplitude')
        ax.set_xlabel('Time [seconds]')
        plt.show()

    def add_to_ax(self, ax: plt.Axes) -> NoReturn:
        """
        Add the point detector to the provided axis as a scatter point.

        Parameters
        ----------
        ax : plt.Axes
            The axis to which the point detector will be added.
        """
        ax.scatter(
            self.p0.x,
            self.p0.y,
            color=self.facecolor,
            label='detector'
        )
