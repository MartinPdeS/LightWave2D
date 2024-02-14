import numpy
from dataclasses import dataclass
from LightWave2D.grid import Grid
from MPSPlots.render2D import SceneList, Axis
from LightWave2D.physics import Physics


class BaseComponent():
    def __post_init__(self):
        self.epsilon_r_mesh = numpy.ones(self.grid.shape)  # Background permittivity

        self.build_mesh()

    def add_to_ax(self, ax: Axis) -> None:
        ax.add_mesh(
            x=self.grid.x_stamp * 1e6,
            y=self.grid.y_stamp * 1e6,
            scalar=self.epsilon_r_mesh.T,
        )

    def plot(self) -> SceneList:
        scene = SceneList(
            unit_size=(4, 4),
            title='FDTD Simulation at time step'
        )

        ax = scene.append_ax(
            x_label=r'x position [$\mu$m]',
            y_label=r'y position [$\mu$m]',
            aspect_ratio='equal',
        )

        self.add_to_ax(ax)

        ax.add_colorbar(colormap='Blues')

        return scene

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


@dataclass()
class Waveguide(BaseComponent):
    grid: Grid
    """ The grid of the simulation mesh """
    width: int | str
    """ Width of the waveguide in grid cells """
    height: int | str
    """ Height of the waveguide in grid cells """
    position: tuple
    """ Starting position of the waveguide """
    epsilon_r: float
    """ Relative permittivity inside the waveguide """

    def build_mesh(self) -> None:
        width_index, height_index = self.interpret_width_height()

        x_index, y_index = self.interpret_position_to_index()

        x_start = x_index
        x_end = x_index + width_index

        y_start = y_index
        y_end = y_index + height_index

        self.epsilon_r_mesh[
            x_start:x_end,
            y_start:y_end
        ] = self.epsilon_r

    def interpret_width_height(self) -> tuple:
        """
        Interprets and returns the value of width (x) and height (y) of the waveguide

        :returns:   The index of width and height
        :rtype:     tuple
        """
        if isinstance(self.width, str) and self.width.lower() == 'full':
            width_index = self.grid.n_x
        else:
            width_index = self.grid.position_to_index(self.width, axis='x')

        if isinstance(self.height, str) and self.height.lower() == 'full':
            height_index = self.grid.n_y
        else:
            height_index = self.grid.position_to_index(self.height, axis='y')

        return int(width_index), int(height_index)


@dataclass()
class Scatterer(BaseComponent):
    grid: Grid
    """ The grid of the simulation mesh """
    position: tuple
    """ Starting position of the scatterer """
    epsilon_r: float
    """ Relative permittivity inside the waveguide """
    radius: float
    """ Radius of the scatterer """

    def build_mesh(self) -> None:
        x0, y0 = self.position

        self.coordinate = self.grid.get_coordinate(x=x0, y=y0)

        distance_mesh = self.grid.get_distance_grid(
            x0=self.coordinate.y,
            y0=self.coordinate.x
        )

        self.idx = distance_mesh < self.radius

        self.epsilon_r_mesh[self.idx] = self.epsilon_r

    def add_to_ax(self, ax: Axis) -> None:
        return ax.add_circle(
            position=(self.coordinate.x, self.coordinate.y),
            radius=self.radius,
            label='scatterer'
        )
# -
