import numpy
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
