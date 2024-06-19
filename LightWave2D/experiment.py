#!/usr/bin/env python
# -*- coding: utf-8 -*-


from typing import Tuple, NoReturn
import numpy
from LightWave2D.physics import Physics
from LightWave2D.grid import Grid
from LightWave2D.components import Waveguide, Circle, Square
from LightWave2D.source import PointSource, VerticalLineSource, LineSource
from LightWave2D.detector import PointDetector
from dataclasses import dataclass
from LightWave2D.pml import PML
import matplotlib.pyplot as plt
from MPSPlots import colormaps
from MPSPlots.render2D import SceneList
import matplotlib.animation as animation


@dataclass
class Experiment:
    """Class representing an FDTD simulation experiment."""

    grid: Grid
    """The grid of the simulation mesh."""

    def __post_init__(self):
        self.sources = []
        self.components = []
        self.detectors = []
        self.Ez_t = numpy.zeros((self.grid.n_steps, *self.grid.shape))
        self.epsilon = numpy.ones(self.grid.shape) * Physics.epsilon_0
        self.pml = None

    def get_gradient(self, field: numpy.ndarray, axis: str) -> numpy.ndarray:
        """
        Compute the gradient of the field along the specified axis.

        Args:
            field (numpy.ndarray): The field to compute the gradient for.
            axis (str): The axis along which to compute the gradient ('x' or 'y').

        Returns:
            numpy.ndarray: The computed gradient.
        """
        if axis == 'x':
            gradient = numpy.diff(field, axis=0) / self.grid.dx
        elif axis == 'y':
            gradient = numpy.diff(field, axis=1) / self.grid.dy
        else:
            raise ValueError("Axis must be 'x' or 'y'.")
        return gradient

    def plot(self) -> SceneList:
        """Create a plot of the FDTD simulation setup."""
        scene = SceneList(unit_size=(6, 6), title='FDTD Simulation at time step')
        ax = scene.append_ax(
            x_label=r'x position [$\mu$m]',
            y_label=r'y position [$\mu$m]',
            aspect_ratio='equal',
            show_legend=True
        )

        if self.pml:
            self.pml.add_to_ax(ax)

        for component in self.components:
            component.add_to_ax(ax)

        for source in self.sources:
            source.add_to_ax(ax)

        for detector in self.detectors:
            detector.add_to_ax(ax)

        ax.add_colorbar(colormap='Blues')
        return scene

    def add_to_component(function):
        def wrapper(self, **kwargs):
            component = function(self, **kwargs)
            self.components.append(component)
            return component
        return wrapper

    def add_to_source(function):
        def wrapper(self, **kwargs):
            source = function(self, **kwargs)
            self.sources.append(source)
            return source
        return wrapper

    def add_to_detector(function):
        def wrapper(self, **kwargs):
            detector = function(self, **kwargs)
            self.detectors.append(detector)
            return detector
        return wrapper

    def add_pml(self, **kwargs) -> PML:
        """Add a Perfectly Matched Layer (PML) to the simulation."""
        self.pml = PML(grid=self.grid, **kwargs)
        return self.pml

    @add_to_component
    def add_circle(self, **kwargs) -> Circle:
        """General method to add a component to the simulation."""
        return Circle(grid=self.grid, **kwargs)

    @add_to_component
    def add_square(self, **kwargs) -> Square:
        """General method to add a component to the simulation."""
        return Square(grid=self.grid, **kwargs)

    @add_to_component
    def add_waveguide(self, **kwargs) -> Waveguide:
        """General method to add a component to the simulation."""
        return Waveguide(grid=self.grid, **kwargs)

    @add_to_source
    def add_vertical_line_source(self, **kwargs) -> VerticalLineSource:
        """General method to add a source to the simulation."""
        return VerticalLineSource(grid=self.grid, **kwargs)

    @add_to_source
    def add_point_source(self, **kwargs) -> PointSource:
        """General method to add a source to the simulation."""
        return PointSource(grid=self.grid, **kwargs)

    @add_to_source
    def add_line_source(self, **kwargs) -> LineSource:
        """General method to add a source to the simulation."""
        return LineSource(grid=self.grid, **kwargs)

    @add_to_detector
    def add_point_detector(self, **kwargs) -> PointDetector:
        """General method to add a detector to the simulation."""
        return PointDetector(grid=self.grid, **kwargs)

    def get_sigma(self) -> Tuple[float, float]:
        """
        Retrieve the sigma values for the PML.

        Returns:
            tuple: Sigma values for x and y directions.
        """
        if self.pml is not None:
            sigma_x, sigma_y = self.pml.sigma_x, self.pml.sigma_y
        else:
            sigma_x = sigma_y = numpy.zeros(self.grid.shape)
        return sigma_x, sigma_y

    def get_epsilon(self) -> numpy.ndarray:
        """
        Construct the epsilon mesh with contributions from all components.

        Returns:
            numpy.ndarray: The epsilon mesh.
        """
        epsilon_r_mesh = numpy.ones(self.grid.shape) * Physics.epsilon_0
        for component in self.components:
            component.add_to_mesh(epsilon_r_mesh)
        return epsilon_r_mesh * Physics.epsilon_0

    def get_field_yee_gradient(self, field: numpy.ndarray) -> Tuple[float, float]:
        """
        Calculate the Yee grid gradient of the field.

        Args:
            field (numpy.ndarray): The field to calculate the gradient for.

        Returns:
            tuple: Gradients along x and y directions.
        """
        d_dx = (field[1:, :] - field[:-1, :]) / self.grid.dx
        d_dy = (field[:, 1:] - field[:, :-1]) / self.grid.dy
        return d_dx, d_dy

    def run_fdtd(self) -> NoReturn:
        """Run the FDTD simulation."""
        Ez = numpy.zeros(self.grid.shape)
        Hx = numpy.zeros(self.grid.shape)
        Hy = numpy.zeros(self.grid.shape)

        sigma_x, sigma_y = self.get_sigma()
        epsilon = self.get_epsilon()

        for iteration, t in enumerate(self.grid.time_stamp):
            mu_factor = self.grid.dt / Physics.mu_0
            eps_factor = self.grid.dt / epsilon

            dEz_dx, dEz_dy = self.get_field_yee_gradient(Ez)
            Hx[:, :-1] -= mu_factor * dEz_dy * (1 - sigma_y[:, :-1] * mu_factor / 2)
            Hy[:-1, :] += mu_factor * dEz_dx * (1 - sigma_x[:-1, :] * mu_factor / 2)

            dEz_dx, dEz_dy = self.get_field_yee_gradient(Ez)
            dHy_dx = (Hy[1:-1, 1:-1] - Hy[:-2, 1:-1]) / self.grid.dx
            dHx_dy = (Hx[1:-1, 1:-1] - Hx[1:-1, :-2]) / self.grid.dy

            Ez[1:-1, 1:-1] += eps_factor[1:-1, 1:-1] * (dHy_dx - dHx_dy)

            for component in self.components:
                component.add_non_linear_effect_to_field(Ez)

            Ez *= (1 - (sigma_x + sigma_y) * eps_factor / 2)

            for source in self.sources:
                source.add_source_to_field(Ez, time=t)

            self.Ez_t[iteration] = Ez

        self.update_detectors()

    def update_detectors(self) -> NoReturn:
        """Update detector data with the field values."""
        for detector in self.detectors:
            detector.update_data(field=self.Ez_t)

    def render_propagation(self, skip_frame: int = 10, dark_colormap: bool = True) -> animation.FuncAnimation:
        """
        Render the propagation of the field as an animation.

        Args:
            skip_frame (int): Number of frames to skip between each rendered frame.
            dark_colormap (bool): Use a dark colormap if True.

        Returns:
            animation.FuncAnimation: The animation of the field propagation.
        """
        colormap = colormaps.poly_red_black_blue if dark_colormap else colormaps.blue_white_red

        scene = SceneList(unit_size=(8, 8))
        ax = scene.append_ax(
            title='FDTD Simulation at time step',
            x_label=r'x position [$\mu$m]',
            y_label=r'x position [$\mu$m]',
            aspect_ratio='equal',
            show_grid=False
        )
        ax.add_colorbar(colormap=colormap)

        initial_field = numpy.zeros(self.Ez_t[0].shape).T
        artist_list = []

        field_artist = ax.add_mesh(
            x=self.grid.x_stamp,
            y=self.grid.y_stamp,
            scalar=initial_field,
            layer_position=-1,
        )
        artist_list.append(field_artist)

        for component in self.components:
            component_artist = component.add_to_ax(ax)
            artist_list.append(component_artist)

        scene._render_()

        max_amplitude = abs(self.Ez_t).max() / 2
        field_artist.mappable.set_clim(vmin=-max_amplitude, vmax=max_amplitude)

        def update(frame) -> list:
            field_t = self.Ez_t[frame].T
            field_artist.mappable.set_array(field_t)
            return [art.mappable for art in artist_list]

        def init_func():
            ax.mpl_ax.set_xticks([])
            ax.mpl_ax.set_yticks([])
            return field_artist.mappable,

        render = animation.FuncAnimation(
            fig=scene._mpl_figure,
            func=update,
            frames=numpy.arange(0, self.grid.n_steps, skip_frame),
            interval=0.2,
            blit=True,
            init_func=init_func
        )
        return render

    def _plot_propagation(self, dark_colormap: bool = True) -> NoReturn:
        """Plot the propagation of the field using matplotlib."""
        colormap = colormaps.blue_black_red if dark_colormap else colormaps.blue_white_red

        fig, ax = plt.subplots(1, 1)
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
        mappable.set_clim(vmin=-max_amplitude, vmax=max_amplitude)

        for iteration, t in enumerate(self.grid.time_stamp):
            field_t = self.Ez_t[iteration].T

            if iteration % 10 == 0:
                ax.set_title(f"Time stamp: {t * 1e9: .3e} [ns]")
                mappable.set_array(field_t)
                fig.canvas.draw()
                fig.canvas.flush_events()
                plt.show(block=False)
