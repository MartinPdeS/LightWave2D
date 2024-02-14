from dataclasses import dataclass, field
import numpy

from LightWave2D.grid import Grid
from MPSPlots.render2D import SceneList, Axis


@dataclass()
class PointDetector():
    grid: Grid
    """ The grid of the simulation mesh """
    position: tuple
    """ Position of the point detector """

    coordinate: object = field(init=False)
    """ Coordinate of the detector """
    data: numpy.ndarray = field(init=False)
    """ Data over time """

    def __post_init__(self):
        self.coordinate = self.grid.get_coordinate(
            x=self.position[0],
            y=self.position[1]
        )

        self.data = numpy.zeros(self.grid.n_steps)

    def update_data(self, field: numpy.ndarray) -> None:
        self.data = field[:, self.coordinate.x_index, self.coordinate.y_index]

    def plot(self) -> SceneList:
        scene = SceneList()

        ax = scene.append_ax()

        ax.add_line(x=self.grid.time_stamp, y=self.data)

        return scene

    def add_to_ax(self, ax: Axis) -> None:
        ax.add_scatter(
            x=self.coordinate.x,
            y=self.coordinate.y,
            color='black',
            marker_size=20,
            label='detector'
        )

