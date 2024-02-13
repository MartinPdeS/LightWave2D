import numpy
from LightWave2D.physics import Physics
from LightWave2D.grid import Grid
from LightWave2D.components import Waveguide, Scatterer
from LightWave2D.source import PointSource, VerticalLineSource, LineSource
from dataclasses import dataclass
from LightWave2D.pml import PML
import matplotlib.pyplot as plt
from MPSPlots import colormaps
from MPSPlots.render2D import SceneList


@dataclass
class Experiment():
    grid: Grid
    """ The grid of the simulation mesh """

    def __post_init__(self):
        self.sources = []
        self.components = []
        self.Ez_t = numpy.zeros((self.grid.n_steps, *self.grid.shape))

        self.epsilon = numpy.ones(self.grid.shape) * Physics.epsilon_0

    def get_gradient(self, field: numpy.ndarray, axis: str) -> numpy.ndarray:
        if axis == 'x':
            array = numpy.diff(field, axis=0)

            array = array
            array /= self.grid.dx

        if axis == 'y':
            array = numpy.diff(field, axis=1)

            array = array
            array /= self.grid.dy

        return array

    def plot(self):
        scene = SceneList(
            unit_size=(4, 4),
            title='FDTD Simulation at time step'
        )

        ax = scene.append_ax(
            x_label=r'x position [$\mu$m]',
            y_label=r'y position [$\mu$m]',
            aspect_ratio='equal',
            show_legend=True
        )

        self.pml.add_to_ax(ax)

        for component in self.components:
            component.add_to_ax(ax)

        for source in self.sources:
            source.add_to_ax(ax)

        ax.add_colorbar(colormap='Blues')

        return scene

    def add_pml(self, *args, **kwargs) -> None:
        pml = PML(*args, grid=self.grid, **kwargs)

        self.pml = pml

    def add_scatterer(self, *args, **kwargs) -> Scatterer:
        component = Scatterer(
            *args,
            grid=self.grid,
            **kwargs,
        )

        self.components.append(component)

        return component

    def add_vertical_line_source(self, *args, **kwargs) -> VerticalLineSource:
        source = VerticalLineSource(
            *args,
            grid=self.grid,
            **kwargs,
        )

        self.sources.append(source)

        return source

    def add_line_source(self, *args, **kwargs) -> LineSource:
        source = LineSource(
            *args,
            grid=self.grid,
            **kwargs,
        )

        self.sources.append(source)

        return source

    def get_sigma(self) -> tuple:
        if self.pml is not None:
            sigma_x = self.pml.sigma_x
            sigma_y = self.pml.sigma_y
        else:
            sigma_x = sigma_y = numpy.zeros(self.grid.shape)

        return sigma_x, sigma_y

    def get_epsilon(self):
        epsilon_r_mesh = numpy.ones(self.grid.shape) * Physics.epsilon_0

        for component in self.components:
            component.add_to_mesh(epsilon_r_mesh)

        return epsilon_r_mesh * Physics.epsilon_0

    def propagate(self) -> None:
        Ez = numpy.zeros(self.grid.shape)
        Hx = numpy.zeros(self.grid.shape)
        Hy = numpy.zeros(self.grid.shape)

        sigma_x, sigma_y = self.get_sigma()

        epsilon = self.get_epsilon()

        for iteration, t in enumerate(self.grid.time_stamp):

            mu_factor: float = self.grid.dt / Physics.mu_0

            eps_factor: float = self.grid.dt / epsilon

            dEz_dx = (Ez[1:, :] - Ez[:-1, :]) / self.grid.dx
            dEz_dy = (Ez[:, 1:] - Ez[:, :-1]) / self.grid.dy

            Hx[:, :-1] -= mu_factor * dEz_dy * (1 - sigma_y[:, :-1] * mu_factor / 2)
            Hy[:-1, :] += mu_factor * dEz_dx * (1 - sigma_x[:-1, :] * mu_factor / 2)

            dHy_dx = (Hy[1:-1, 1:-1] - Hy[:-2, 1:-1]) / self.grid.dx
            dHx_dy = (Hx[1:-1, 1:-1] - Hx[1:-1, :-2]) / self.grid.dy

            Ez[1:-1, 1:-1] += eps_factor[1:-1, 1:-1] * (dHy_dx - dHx_dy)

            # chi_2 = 1
            # Ez += self.grid.dt**2 / (epsilon * Physics.mu_0) * chi_2 * Ez**2

            Ez *= (1 - (sigma_x + sigma_y) * eps_factor / 2)

            for source in self.sources:
                source.add_source_to_field(field=Ez, time=t)

            self.Ez_t[iteration] = Ez

    def plot_propgation(self, dark_colormap: bool = True) -> None:
        colormap = colormaps.blue_black_red if dark_colormap else colormaps.blue_white_red

        figure, ax = plt.subplots(1, 1)
        ax.set_title('FDTD Simulation at time step')
        ax.set_xlabel(r'x position [$\mu$m]')
        ax.set_ylabel(r'y position [$\mu$m]')

        initial_field = numpy.zeros(self.Ez_t[0].shape)

        mappable = ax.pcolormesh(
            self.grid.x_stamp * 1e6,
            self.grid.y_stamp * 1e6,
            initial_field.T,
            cmap=colormap,
        )
        ax.set_aspect('equal')

        max_amplitude = abs(self.Ez_t).max() / 6

        for iteration, t in enumerate(self.grid.time_stamp):
            field_t = self.Ez_t[iteration].T

            if iteration % 10 == 0:

                ax.set_title(f"Time stamp: {t * 1e9: .3e} [ns]")

                mappable.set_array(field_t)

                mappable.set_clim(
                    vmin=-max_amplitude,
                    vmax=max_amplitude
                )

                figure.canvas.draw()
                figure.canvas.flush_events()

                plt.show(block=False)

# -
