import numpy
from dataclasses import dataclass
from LightWave2D.grid import Grid

from MPSPlots.render2D import SceneList, Axis


@dataclass()
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

    def add_to_ax(self, ax: Axis) -> None:
        ax.add_mesh(
            x=self.grid.x_stamp,
            y=self.grid.y_stamp,
            scalar=self.sigma_y.T + self.sigma_x.T
        )

    def plot(self) -> SceneList:
        scene = SceneList()

        ax = scene.append_ax()

        self.add_to_ax(ax)

        return scene

# -
