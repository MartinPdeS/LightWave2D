#!/usr/bin/env python
# -*- coding: utf-8 -*-


from typing import Tuple, Optional, Union, List
import numpy
from LightWave2D.physics import Physics
from LightWave2D.grid import Grid
from LightWave2D import components
from LightWave2D import source
from LightWave2D.detector import PointDetector
from LightWave2D.pml import PML
from MPSPlots import colormaps
import matplotlib.animation as animation
from pydantic.dataclasses import dataclass
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
from MPSPlots.styles import mps
from LightWave2D.helper import _plot_helper

from LightWave2D.binary import fdtd_simulation

config_dict = dict(
    kw_only=True,
    slots=True,
    extra='forbid',
    arbitrary_types_allowed=True
)


@dataclass(config=config_dict)
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

        Parameters
        ----------
        field : numpy.ndarray)
            The field to compute the gradient for.
        axis : str
            The axis along which to compute the gradient ('x' or 'y').

        Returns
        -------
        numpy.ndarray
            The computed gradient.
        """
        if axis == 'x':
            gradient = numpy.diff(field, axis=0) / self.grid.dx
        elif axis == 'y':
            gradient = numpy.diff(field, axis=1) / self.grid.dy
        else:
            raise ValueError("Axis must be 'x' or 'y'.")
        return gradient

    @_plot_helper
    def plot(self, ax: plt.Axes, unit_size: int = 8, colormap: Optional[Union[str, object]] = 'Blues') -> None:
        """
        Generates a plot of the FDTD simulation setup using a specified colormap.

        This function initializes a plotting scene and adds elements of the FDTD simulation
        such as components, sources, detectors, and optionally the PML layers. It adjusts
        the axis properties and attaches a colorbar based on the selected colormap.

        Parameters
        ----------
        colormap : Optional[Union[str, object]])
            The colormap to use for the plot. If 'None' is passed, a default dark-themed colormap is used. Default is 'Blues'.

        """
        # Add PML layers to the plot if present
        if self.pml:
            self.pml.add_to_ax(ax)

        for component in [*self.components, *self.sources, *self.detectors]:
            component.add_to_ax(ax)

        ax.legend()
        ax.autoscale_view()

    def add_to_component(function):
        def wrapper(self, **kwargs):
            component = function(self, **kwargs)
            self.components.append(component)
            return component
        wrapper.__doc__ = function.__doc__
        return wrapper

    def add_to_source(function):
        def wrapper(self, **kwargs):
            source = function(self, **kwargs)
            self.sources.append(source)
            return source
        wrapper.__doc__ = function.__doc__
        return wrapper

    def add_to_detector(function):
        def wrapper(self, **kwargs):
            detector = function(self, **kwargs)
            self.detectors.append(detector)
            return detector
        wrapper.__doc__ = function.__doc__
        return wrapper

    def add_pml(self, **kwargs) -> PML:
        """Add a Perfectly Matched Layer (PML) to the simulation."""
        self.pml = PML(grid=self.grid, **kwargs)
        return self.pml

    @add_to_component
    def add_circle(self, **kwargs) -> components.Circle:
        """
        Method to add a components.Circle to the simulation.
        """
        return components.Circle(grid=self.grid, **kwargs)

    @add_to_component
    def add_ellipse(self, **kwargs) -> components.Ellipse:
        """
        Method to add a components.Ellipse to the simulation.
        """
        return components.Ellipse(grid=self.grid, **kwargs)

    @add_to_component
    def add_square(self, **kwargs) -> components.Square:
        """
        open()
        Method to add a components.Square to the simulation.
        """
        return components.Square(grid=self.grid, **kwargs)

    @add_to_component
    def add_triangle(self, **kwargs) -> components.Triangle:
        """
        Method to add a components.Triangle to the simulation.
        """
        return components.Triangle(grid=self.grid, **kwargs)

    @add_to_component
    def add_lense(self, **kwargs) -> components.Lense:
        """
        Method to add a components.Lense to the simulation.
        """
        return components.Lense(grid=self.grid, **kwargs)

    @add_to_component
    def add_grating(self, **kwargs) -> components.Grating:
        """
        Method to add a components.Grating to the simulation.
        """
        return components.Grating(grid=self.grid, **kwargs)

    @add_to_component
    def add_ring_resonator(self, **kwargs) -> components.RingResonator:
        """
        Method to add a components.RingResonator to the simulation.
        """
        return components.RingResonator(grid=self.grid, **kwargs)

    @add_to_component
    def add_waveguide(self, **kwargs) -> components.Waveguide:
        """
        Method to add a components.Waveguide to the simulation.
        """
        return components.Waveguide(grid=self.grid, **kwargs)

    @add_to_source
    def add_point_source(self, **kwargs) -> source.PointSource:
        """
        Method to add a source.PointSource to the simulation.
        """
        return source.PointSource(grid=self.grid, **kwargs)

    @add_to_source
    def add_point_impulsion(self, **kwargs) -> source.PointImpulsion:
        """
        Method to add a source.Impulsion to the simulation.
        """
        return source.PointImpulsion(grid=self.grid, **kwargs)

    @add_to_source
    def add_line_source(self, **kwargs) -> source.LineSource:
        """
        Method to add a source.LineSource to the simulation.
        """
        return source.LineSource(grid=self.grid, **kwargs)

    @add_to_source
    def add_line_impulsion(self, **kwargs) -> source.LineImpulsion:
        """
        Method to add a source.LineSource to the simulation.
        """
        return source.LineImpulsion(grid=self.grid, **kwargs)

    @add_to_detector
    def add_point_detector(self, **kwargs) -> PointDetector:
        """
        Method to add a PointDetector to the simulation.
        """
        return PointDetector(grid=self.grid, **kwargs)

    def get_sigma(self) -> Tuple[numpy.ndarray, numpy.ndarray]:
        """
        Retrieve the sigma values for the PML.

        Returns:
            tuple: Sigma values for x and y directions.
        """
        if self.pml is not None:
            sigma_x, sigma_y = self.pml.sigma_x, self.pml.sigma_y
        else:
            sigma_x = sigma_y = numpy.zeros(self.grid.shape)

        for component in self.components:
            component.add_to_sigma_mesh(sigma_x)
            component.add_to_sigma_mesh(sigma_y)

        return sigma_x, sigma_y

    def get_epsilon(self) -> numpy.ndarray:
        """
        Construct the epsilon mesh with contributions from all components.

        Returns
        -------
        numpy.ndarray
            The epsilon mesh.
        """
        epsilon_r_mesh = numpy.ones(self.grid.shape)
        for component in self.components:
            component.add_to_epsilon_r_mesh(epsilon_r_mesh)

        return epsilon_r_mesh * Physics.epsilon_0

    def run_fdtd(self) -> None:
        r"""
        Run the Finite-Difference Time-Domain (FDTD) simulation.

        This method updates the electric field (Ez) and magnetic fields (Hx, Hy) over time
        based on Maxwell's equations using the FDTD method. It incorporates the effects
        of absorption, sources, and non-linear interactions.

        Maxwell's equations in 2D for non-magnetic media:

        .. math::
            \frac{\partial H_x}{\partial t} = -\frac{1}{\mu} \frac{\partial E_z}{\partial y} \\[10pt]
            \frac{\partial H_y}{\partial t} = \frac{1}{\mu} \frac{\partial E_z}{\partial x} \\[10pt]
            \frac{\partial E_z}{\partial t} = \frac{1}{\epsilon} \left( \frac{\partial H_y}{\partial x} - \frac{\partial H_x}{\partial y} \right) - \sigma E_z

        Attributes
        ----------
        Ez : numpy.ndarray
            The electric field in the z-direction.
        Hx : numpy.ndarray
            The magnetic field in the x-direction.
        Hy : numpy.ndarray
            The magnetic field in the y-direction.
        sigma_x : numpy.ndarray
            Conductivity in the x direction.
        sigma_y : numpy.ndarray
            Conductivity in the y direction.
        epsilon : numpy.ndarray
            Permittivity of the grid.
        mu_factor : float
            Precomputed factor for the magnetic field update.
        eps_factor : numpy.ndarray
            Precomputed factor for the electric field update.

        Returns
        -------
        None
            This method does not return any value; it updates the simulation fields.
        """
        self.Ez_t = numpy.zeros((self.grid.n_steps, *self.grid.shape))

        sigma_x, sigma_y = self.get_sigma()
        epsilon = self.get_epsilon()

        fdtd_simulation.run_fdtd(
            Ez=self.Ez_t,
            time_stamp=self.grid.time_stamp,
            sigma_x=sigma_x,
            sigma_y=sigma_y,
            epsilon=epsilon,
            gamma=epsilon * 0,
            n2=epsilon * 0,
            dt=self.grid.dt,
            mu_0=Physics.mu_0,
            n_steps=self.grid.n_steps,
            dx=self.grid.dx,
            dy=self.grid.dy,
            nx=self.grid.n_x,
            ny=self.grid.n_y,
            sources=[s.binding for s in self.sources]
        )

    def _run_fdtd(self) -> None:
        r"""
        Legacy function to run the FDTD simulation.

        This method updates the electric field (Ez) and magnetic fields (Hx, Hy) over time
        based on Maxwell's equations using the FDTD method. It also includes the effects
        of absorption, sources, and non-linear interactions.

        Maxwell's equations in 2D for non-magnetic media:

        .. math::
            \frac{\partial H_x}{\partial t} = -\frac{1}{\mu} \frac{\partial E_z}{\partial y} \\[10pt]
            \frac{\partial H_y}{\partial t} = \frac{1}{\mu} \frac{\partial E_z}{\partial x} \\[10pt]
            \frac{\partial E_z}{\partial t} = \frac{1}{\epsilon} \left( \frac{\partial H_y}{\partial x} - \frac{\partial H_x}{\partial y} \right) - \sigma E_z

        Attributes
        ----------
        Ez : numpy.ndarray
            The electric field in the z-direction.
        Hx : numpy.ndarray
            The magnetic field in the x-direction.
        Hy : numpy.ndarray
            The magnetic field in the y-direction.
        sigma_x : numpy.ndarray
            Conductivity in the x direction.
        sigma_y : numpy.ndarray
            Conductivity in the y direction.
        epsilon : numpy.ndarray
            Permittivity of the grid.
        mu_factor : float
            Precomputed factor for the magnetic field update.
        eps_factor : numpy.ndarray
            Precomputed factor for the electric field update.

        Returns
        -------
        None
            This method does not return any value; it updates the simulation fields.
        """
        Ez = numpy.zeros(self.grid.shape)
        Hx = numpy.zeros(self.grid.shape)
        Hy = numpy.zeros(self.grid.shape)

        sigma_x, sigma_y = self.get_sigma()
        epsilon = self.get_epsilon()
        mu_factor = self.grid.dt / Physics.mu_0
        eps_factor = self.grid.dt / epsilon

        for iteration, t in enumerate(self.grid.time_stamp):
            dEz_dx = (Ez[1:, :] - Ez[:-1, :]) / self.grid.dx
            dEz_dy = (Ez[:, 1:] - Ez[:, :-1]) / self.grid.dy

            Hx[:, :-1] -= mu_factor * dEz_dy * (1 - sigma_y[:, :-1] * mu_factor / 2)
            Hy[:-1, :] += mu_factor * dEz_dx * (1 - sigma_x[:-1, :] * mu_factor / 2)

            dHy_dx = (Hy[1:-1, 1:-1] - Hy[:-2, 1:-1]) / self.grid.dx
            dHx_dy = (Hx[1:-1, 1:-1] - Hx[1:-1, :-2]) / self.grid.dy

            Ez[1:-1, 1:-1] += eps_factor[1:-1, 1:-1] * (dHy_dx - dHx_dy)

            absorption_factor = 1 - (sigma_x + sigma_y) * eps_factor / 2
            absorption_factor = numpy.clip(absorption_factor, 0, 1)
            Ez *= absorption_factor

            for component in self.components:
                Ez = component.add_non_linear_effect_to_field(Ez)

            for element in self.sources:
                element.add_source_to_field(Ez, time=t)

            self.Ez_t[iteration] = Ez

        for detector in self.detectors:
            detector.update_data(field=self.Ez_t)

    @_plot_helper
    def plot_frame(
            self,
            ax: plt.Axes,
            frame_number: int,
            scale_max: float = 5,
            unit_size: int = 6,
            show_intensity: bool = False,
            colormap: Optional[Union[str, object]] = colormaps.polytechnique.blue_black_red) -> None:
        """
        Plot a specific frame from the FDTD simulation.

        This method visualizes the electric field distribution for a specified frame, including
        the components, sources, and detectors present in the simulation.

        Parameters
        ----------
        frame_number : int
            The index of the frame to be visualized.
        scale_max : float, optional
            The maximum scale factor for the color limits of the field. Default is 5.
        unit_size : int, optional
            The base unit size for the plot. Default is 6.
        show_intensity : bool, optional
            If True, displays the intensity instead of the amplitude. Default is False.
        colormap : Optional[Union[str, object]], optional
            The colormap used for visualization. Default is a blue-black-red colormap from the Polytechnique collection.

        Returns
        -------
        None
            This method does not return any value; it displays the plot.
        """
        if show_intensity:
            data = abs(self.Ez_t[frame_number].T)
        else:
            data = self.Ez_t[frame_number].T

        image = ax.pcolormesh(
            self.grid.x_stamp,
            self.grid.y_stamp,
            data,
            cmap=colormap
        )

        for component in [*self.components, *self.sources, *self.detectors]:
            component.add_to_ax(ax)

        vmin, vmax = image.get_clim()
        max_diff = max(abs(vmin), abs(vmax)) / scale_max
        image.set_clim([-max_diff, max_diff])

        plt.colorbar(image)

    @_plot_helper
    def save_frame_as_image(
            self,
            ax: plt.Axes,
            frame_number: int,
            filename: str,
            scale_max: float = 5,
            dpi: int = 200,
            show_intensity: bool = False,
            colormap: Optional[Union[str, object]] = colormaps.polytechnique.blue_black_red) -> None:
        """
        Save a specific frame from the FDTD simulation as an image.

        This method plots a specific frame of the simulation using the specified colormap
        and saves it as an image file with the given resolution.

        Parameters
        ----------
        frame_number : int
            The index of the frame to be saved.
        filename : str
            The file path where the image will be saved.
        scale_max : float, optional
            The maximum scale factor for the color limits of the image. Default is 5.
        figsize : tuple, optional
            The base unit size for the plot. Default is 6.
        dpi : int, optional
            The resolution of the saved image in dots per inch. Default is 200.
        show_intensity : bool, optional
            If True, displays intensity instead of amplitude. Default is False.
        colormap : Optional[Union[str, object]], optional
            The colormap used for visualizing the data. Default is a predefined blue-black-red colormap.

        Returns
        -------
        None
            This method does not return any value, but saves an image file at the specified path.
        """
        if show_intensity:
            data = abs(self.Ez_t[frame_number].T)
        else:
            data = self.Ez_t[frame_number].T

        image = ax.pcolormesh(
            self.grid.x_stamp,
            self.grid.y_stamp,
            data,
            cmap=colormap
        )

        for component in [*self.components, *self.sources, *self.detectors]:
            component.add_to_ax(ax)

        vmin, vmax = image.get_clim()
        max_diff = max(abs(vmin), abs(vmax)) / scale_max
        image.set_clim([-max_diff, max_diff])

        plt.savefig(filename, dpi=dpi)

    def get_figure_ax(self, unit_size: int = 6) -> Tuple:
        """
        Get a matplotlib figure and axis for plotting.

        Parameters
        ----------
        unit_size : int, optional
            The base unit size for scaling the plot. Default is 6.

        Returns
        -------
        Tuple
            A tuple containing the matplotlib figure and axis objects.
        """
        figsize = int(unit_size), int(unit_size * self.grid.size_y / self.grid.size_x)
        figure, ax = plt.subplots(1, 1, figsize=figsize)

        ax.set_xlabel(r'x position [$\mu$m]')
        ax.set_ylabel(r'y position [$\mu$m]')
        ax.set_aspect('equal')

        ticks_x = ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(x / 1e-6))
        ax.xaxis.set_major_formatter(ticks_x)

        ticks_y = ticker.FuncFormatter(lambda y, pos: '{0:g}'.format(y / 1e-6))
        ax.yaxis.set_major_formatter(ticks_y)

        return figure, ax

    def render_propagation(
            self,
            skip_frame: int = 10,
            scale_max: float = 1,
            unit_size: int = 6,
            auto_adjust_clim: bool = False,
            fps: int = 10,
            colormap: Optional[Union[str, object]] = colormaps.blue_black_red) -> animation.FuncAnimation:
        """
        Render an animation of the field propagation.

        This method sets up the scene, initializes the field display, and creates
        an animation showing the evolution of the field over time.

        Parameters
        ----------
        skip_frame : int, optional
            The number of time steps to skip between frames in the animation. Default is 10.
        scale_max : float, optional
            The maximum scale factor for the color limits of the field amplitude. Default is 1.
        unit_size : int, optional
            The base unit size for scaling the plot elements. Default is 6.
        auto_adjust_clim : bool, optional
            If True, automatically adjusts color limits based on field amplitude for each frame. Default is False.
        fps : int, optional
            The frames per second for the animation. Default is 10.
        colormap : Optional[Union[str, object]], optional
            The colormap used for visualizing the data. Default is a predefined blue-black-red colormap.

        Returns
        -------
        animation.FuncAnimation
            The animation object that can be displayed or saved.
        """
        with plt.style.context(mps):
            figure, ax = self.get_figure_ax(unit_size=unit_size)

            # Initialize the field display
            initial_field = numpy.zeros(self.Ez_t[0].shape).T
            field_artist = ax.pcolormesh(
                self.grid.x_stamp,
                self.grid.y_stamp,
                initial_field,
                cmap=colormap
            )

            title = ax.text(
                x=0.85,
                y=.9,
                s="",
                transform=ax.transAxes,
                ha="center",
                color='white'
            )

            # Store all artists for updating
            artist_list = [field_artist]

            # Add other components to the axis and their artists to the list
            for component in self.components:
                artist_list.append(component.add_to_ax(ax))

            max_amplitude = abs(self.Ez_t).max() / scale_max
            field_artist.set_clim(vmin=-max_amplitude, vmax=max_amplitude)

        def update(frame) -> List:
            """
            Update function for the animation; called for each frame.

            Parameters
            ----------
            frame : int
                The current frame number.

            Returns
            -------
            List
                A list of updated artists for the animation.
            """
            time = self.grid.time_stamp[frame]
            field_t = self.Ez_t[frame].T
            field_artist.set_array(field_t)

            if auto_adjust_clim:
                max_amplitude = abs(field_t).max() / scale_max
                field_artist.set_clim(vmin=-max_amplitude, vmax=max_amplitude)

            title.set_text(f'time: {time:.1e}')

            return *artist_list, title,

        def init_func():
            """
            Initialization function for the animation; called at the start.

            Returns
            -------
            Tuple
                A tuple containing the initial field artist and title.
            """
            time = 0
            title.set_text(f'time: {time:.1e}')
            ax.set_xticks([])
            ax.set_yticks([])
            return field_artist, title,

        render = animation.FuncAnimation(
            fig=figure,
            func=update,
            frames=numpy.arange(0, self.grid.n_steps, skip_frame),
            interval=1000 / fps,
            blit=True,
            init_func=init_func
        )

        return render

    def save_propagation(self, filename: str, writer: str = 'Pillow', fps: int = 10, **kwargs) -> animation.FuncAnimation:
        """
        Save the field propagation animation to a file.

        This method generates an animation of the electric field propagation and saves it to
        the specified file using the given writer and frame rate.

        Parameters
        ----------
        filename : str
            The name of the file to save the animation.
        writer : str, optional
            The writer used for saving the animation. Default is 'Pillow'.
        fps : int, optional
            The frames per second for the animation. Default is 10.
        **kwargs
            Additional keyword arguments passed to the render_propagation method.

        Returns
        -------
        animation.FuncAnimation
            The generated animation object.
        """
        animation = self.render_propagation(**kwargs)
        animation.save(filename, writer=writer, fps=fps)
        return animation

    def show_propagation(self, **kwargs) -> animation.FuncAnimation:
        """
        Display the field propagation animation.

        This method generates and displays an animation of the electric field propagation.

        Parameters
        ----------
        **kwargs
            Additional keyword arguments passed to the render_propagation method.

        Returns
        -------
        animation.FuncAnimation
            The generated animation object.
        """
        animation = self.render_propagation(**kwargs)
        plt.show()
        return animation

# -
