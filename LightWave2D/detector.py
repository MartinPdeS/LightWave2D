from dataclasses import dataclass, field
import numpy

from LightWave2D.grid import Grid
from MPSPlots.render2D import SceneList, Axis

import cv2


@dataclass
class CircularDetector():
    grid: Grid
    """ The grid of the simulation mesh """
    position: tuple
    """ Position of the point detector """
    radius: float
    """ Radius of the detector """

    data: numpy.ndarray = field(init=False)
    """ Data over time """

    object_idx: object = field(init=False)

    def __post_init__(self):
        self.position = self.grid.get_coordinate(
            x=self.position[0],
            y=self.position[1]
        )

        self.construct_object()

    def construct_object(self) -> None:
        radius_indexes = self.grid.get_coordinate(x=self.radius, y=self.radius)

        self.object_idx = numpy.zeros(shape=self.grid.shape, dtype=numpy.uint8)

        cv2.ellipse(
            img=self.object_idx,
            center=(self.position.y_index, self.position.x_index),
            axes=(radius_indexes.x_index, radius_indexes.y_index),
            angle=0,
            startAngle=0,
            endAngle=360,
            color=(255, 255, 255),
        )

        self.object_idx = self.object_idx.astype(bool)

        self.object_coordinate_index = numpy.argwhere(self.object_idx == 1).T

        self.angle_list = numpy.arctan2(
            self.object_coordinate_index[0, :] - self.position.x_index,
            self.object_coordinate_index[1, :] - self.position.y_index
        )

    def update_data(self, field: numpy.ndarray) -> None:
        self.data = field[:, self.object_idx != 0]

    def plot_data(self, slc: int | slice = -1) -> SceneList:
        scene = SceneList(unit_size=(5, 5))

        ax = scene.append_ax(projection='polar')
        data = abs(self.data[slc]).sum(axis=0)

        ax.add_scatter(x=self.angle_list, y=data)

        return scene

    def plot(self) -> SceneList:
        scene = SceneList()

        ax = scene.append_ax(aspect_ratio='equal')

        self.add_to_ax(ax)

        return scene

    def add_to_ax(self, ax: Axis) -> None:
        ax.add_circle(
            position=(self.position.x, self.position.y),
            radius=self.radius,
            label='detector',
            facecolor='none',
            edgecolor='black'
        )


@dataclass()
class PointDetector():
    grid: Grid
    """ The grid of the simulation mesh """
    position: tuple
    """ Position of the point detector """

    data: numpy.ndarray = field(init=False)
    """ Data over time """

    def __post_init__(self):
        self.position = self.grid.get_coordinate(
            x=self.position[0],
            y=self.position[1]
        )

        self.data = numpy.zeros(self.grid.n_steps)

    def update_data(self, field: numpy.ndarray) -> None:
        self.data = field[:, self.position.x_index, self.position.y_index]

    def plot_data(self) -> SceneList:
        scene = SceneList()

        ax = scene.append_ax()

        ax.add_line(x=self.grid.time_stamp, y=self.data)

        return scene

    def add_to_ax(self, ax: Axis) -> None:
        ax.add_scatter(
            x=self.position.x,
            y=self.position.y,
            color='black',
            marker_size=20,
            label='detector'
        )

