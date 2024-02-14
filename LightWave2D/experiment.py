import numpy
from LightWave2D.physics import Physics
from LightWave2D.grid import Grid
from LightWave2D.components import Waveguide, Scatterer
from LightWave2D.source import PointSource, VerticalLineSource, LineSource
from LightWave2D.detector import PointDetector
from dataclasses import dataclass
from LightWave2D.pml import PML
import matplotlib.pyplot as plt
from MPSPlots import colormaps
from MPSPlots.render2D import SceneList
import matplotlib.animation as animation


@dataclass
class Experiment():
    grid: Grid
    """ The grid of the simulation mesh """

    def __post_init__(self):
        self.sources = []
        self.components = []
        self.detector_list = []
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
            unit_size=(6, 6),
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

        for detector in self.detector_list:
            detector.add_to_ax(ax)

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

    def add_detector(self, *args, **kwargs) -> PointDetector:
        detector = PointDetector(*args, grid=self.grid, **kwargs)

        self.detector_list.append(detector)

    def get_sigma(self) -> tuple:
        if self.pml is not None:
            sigma_x = self.pml.sigma_x
            sigma_y = self.pml.sigma_y
        else:
            sigma_x = sigma_y = numpy.zeros(self.grid.shape)

        return sigma_x, sigma_y

    def get_epsilon(self) -> numpy.ndarray:
        epsilon_r_mesh = numpy.ones(self.grid.shape) * Physics.epsilon_0

        for component in self.components:
            component.add_to_mesh(epsilon_r_mesh)

        return epsilon_r_mesh * Physics.epsilon_0

    def get_field_yee_gradient(self, field: numpy.ndarray) -> tuple:
        d_dx = (field[1:, :] - field[:-1, :]) / self.grid.dx

        d_dy = (field[:, 1:] - field[:, :-1]) / self.grid.dy

        return d_dx, d_dy

    def run_fdtd(self) -> None:
        Ez = numpy.zeros(self.grid.shape)
        Hx = numpy.zeros(self.grid.shape)
        Hy = numpy.zeros(self.grid.shape)

        sigma_x, sigma_y = self.get_sigma()

        epsilon: numpy.ndarray = self.get_epsilon()

        for iteration, t in enumerate(self.grid.time_stamp):

            mu_factor: float = self.grid.dt / Physics.mu_0

            eps_factor: float = self.grid.dt / epsilon

            dEz_dx, dEz_dy = self.get_field_yee_gradient(field=Ez)

            Hx[:, :-1] -= mu_factor * dEz_dy * (1 - sigma_y[:, :-1] * mu_factor / 2)
            Hy[:-1, :] += mu_factor * dEz_dx * (1 - sigma_x[:-1, :] * mu_factor / 2)

            dEz_dx, dEz_dy = self.get_field_yee_gradient(field=Ez)

            dHy_dx = (Hy[1:-1, 1:-1] - Hy[:-2, 1:-1]) / self.grid.dx
            dHx_dy = (Hx[1:-1, 1:-1] - Hx[1:-1, :-2]) / self.grid.dy

            Ez[1:-1, 1:-1] += eps_factor[1:-1, 1:-1] * (dHy_dx - dHx_dy)

            for component in self.components:
                component.add_non_linear_effect_to_field(field=Ez)

            Ez *= (1 - (sigma_x + sigma_y) * eps_factor / 2)

            for source in self.sources:
                source.add_source_to_field(field=Ez, time=t)

            self.Ez_t[iteration] = Ez

        self.update_detectors()

    def update_detectors(self) -> None:
        for detector in self.detector_list:
            detector.update_data(field=self.Ez_t)

    def render_propagtion(self, skip_frame: int = 5, dark_colormap: bool = True) -> animation.FuncAnimation:
        colormap = colormaps.blue_black_red if dark_colormap else colormaps.blue_white_red

        scene = SceneList(
            unit_size=(8, 8),
        )

        ax = scene.append_ax(
            title='FDTD Simulation at time step',
            x_label=r'x position [$\mu$m]',
            y_label=r'x position [$\mu$m]',
            aspect_ratio='equal'
        )

        ax.add_colorbar(colormap=colormap)

        initial_field = numpy.zeros(self.Ez_t[0].shape).T

        artist_list = []

        field_artist = ax.add_mesh(
            x=self.grid.x_stamp,
            y=self.grid.y_stamp,
            scalar=initial_field,
            layer_position=0,
        )

        artist_list.append(field_artist)

        for component in self.components:
            component_artist = component.add_to_ax(ax)

            artist_list.append(component_artist)

        scene._render_()

        max_amplitude = abs(self.Ez_t).max() / 2

        field_artist.mappable.set_clim(
            vmin=-max_amplitude,
            vmax=max_amplitude
        )

        def update(frame) -> list:
            field_t = self.Ez_t[frame].T

            field_artist.mappable.set_array(field_t)

            mappable_list = [art.mappable for art in artist_list]

            return mappable_list

        def init_func():
            return field_artist.mappable,

        render = animation.FuncAnimation(
            fig=scene._mpl_figure,
            func=update,
            frames=numpy.arange(0, self.grid.n_steps, skip_frame),
            interval=0,
            blit=True,
            init_func=init_func
        )

        plt.show()

        return render

    def plot_propgation(self, dark_colormap: bool = True) -> None:
        colormap = colormaps.blue_black_red if dark_colormap else colormaps.blue_white_red

        figure, ax = plt.subplots(1, 1)
        ax.set_title('FDTD Simulation at time step')
        ax.set_xlabel(r'x position [$\mu$m]')
        ax.set_ylabel(r'y position [$\mu$m]')

        initial_field = numpy.zeros(self.Ez_t[0].shape)

        mappable = ax.pcolormesh(
            self.grid.x_stamp,
            self.grid.y_stamp,
            initial_field.T,
            shading='auto',
            cmap=colormap,
        )
        ax.set_aspect('equal')

        max_amplitude = abs(self.Ez_t).max() / 6

        mappable.set_clim(
            vmin=-max_amplitude,
            vmax=max_amplitude
        )

        for iteration, t in enumerate(self.grid.time_stamp):
            field_t = self.Ez_t[iteration].T

            if iteration % 10 == 0:
                ax.set_title(f"Time stamp: {t * 1e9: .3e} [ns]")

                mappable.set_array(field_t)

                figure.canvas.draw()
                figure.canvas.flush_events()

                plt.show(block=False)

# -
