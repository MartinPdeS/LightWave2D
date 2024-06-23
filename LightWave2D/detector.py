#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Tuple, Union, NoReturn
from dataclasses import field
import numpy
from LightWave2D.grid import Grid
from MPSPlots.render2D import SceneList
import shapely.geometry as geo
from matplotlib.path import Path
import cv2
from pydantic.dataclasses import dataclass
from LightWave2D.components.base_class import BaseComponent
import matplotlib.pyplot as plt

config_dict = dict(
    kw_only=True,
    slots=True,
    extra='forbid',
    arbitrary_types_allowed=True
)


@dataclass(config=config_dict)
class PointDetector(BaseComponent):
    """
    Represents a point detector within a simulation grid.

    Attributes:
        grid (Grid): The simulation mesh grid.
        position (Tuple[float | str, float | str]): The (x, y) coordinates of the point detector on the grid.
        data (numpy.ndarray): The data collected by the detector over time.
    """
    grid: Grid
    position: Union[Tuple[float | str, float | str]]
    data: numpy.ndarray = field(init=False)
    facecolor: str = 'blue'

    def __post_init__(self):
        """
        Initialize the PointDetector by converting the given position into
        grid coordinates and initializing the data array.
        """
        x, y = self.position

        self.p0 = self.grid.get_coordinate(x=x, y=y)

        self.polygon = geo.Point(self.p0.x, self.p0.y)

        self.path = Path(self.polygon.coords)

        self.data = numpy.zeros(self.grid.n_steps)

    def update_data(self, field: numpy.ndarray) -> NoReturn:
        """
        Update the detector data based on the provided field values.

        Parameters:
            field (numpy.ndarray): The field values to update the detector data.
        """
        self.data = field[:, self.p0.x_index, self.p0.y_index]

    def plot_data(self) -> SceneList:
        """
        Plot the detector data over time.

        Returns:
            SceneList: A scene list containing the plot.
        """
        scene = SceneList()
        ax = scene.append_ax()
        ax.add_line(x=self.grid.time_stamp, y=self.data)
        return scene

    def add_to_ax(self, ax: plt.axis) -> NoReturn:
        """
        Add the scatterer to the provided axis as a circle.

        Args:
            ax (Axis): The axis to which the scatterer will be added.
        """
        ax.scatter(
            self.p0.x,
            self.p0.y,
            color=self.facecolor
        )


