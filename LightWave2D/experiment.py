#!/usr/bin/env python
# -*- coding: utf-8 -*-


from typing import Tuple, Optional, Union, List
import numpy
import matplotlib.animation as animation
from pydantic.dataclasses import dataclass
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
from MPSPlots.styles import mps
from MPSPlots import colormaps
from MPSPlots import helper

from LightWave2D.physics import Physics
from LightWave2D.grid import Grid
from LightWave2D import components
from LightWave2D import source
from LightWave2D.detector import PointDetector
from LightWave2D.pml import PML
from LightWave2D.helper import plot_helper
from LightWave2D.binary import interface_simulator
from LightWave2D.utils import config_dict


@dataclass(config=config_dict, kw_only=True)
class Experiment(interface_simulator.FDTDSimulator):
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

        super().__init__()

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

    @plot_helper
    def plot(self, ax: plt.Axes, ) -> None:
        """
        Generates a plot of the FDTD simulation setup using a specified colormap.

        This function initializes a plotting scene and adds elements of the FDTD simulation
        such as components, sources, detectors, and optionally the PML layers. It adjusts
        the axis properties and attaches a colorbar based on the selected colormap.

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
    def add_point_source(self, **kwargs) -> source.PointWaveSource:
        """
        Method to add a source.PointSource to the simulation.
        """
        return source.PointWaveSource(grid=self.grid, **kwargs)

    @add_to_source
    def add_point_impulsion(self, **kwargs) -> source.PointPulseSource:
        """
        Method to add a source.Impulsion to the simulation.
        """
        return source.PointPulseSource(grid=self.grid, **kwargs)

    @add_to_source
    def add_line_source(self, **kwargs) -> source.LineWaveSource:
        """
        Method to add a source.LineSource to the simulation.
        """
        return source.LineWaveSource(grid=self.grid, **kwargs)

    @add_to_source
    def add_line_impulsion(self, **kwargs) -> source.LinePulseSource:
        """
        Method to add a source.LineSource to the simulation.
        """
        return source.LinePulseSource(grid=self.grid, **kwargs)

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

    def run(self) -> None:
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

        self._cpp_set_config(
            dt=self.grid.dt.to('second').magnitude,
            dx=self.grid.dx.to('meter').magnitude,
            dy=self.grid.dy.to('meter').magnitude,
            nx=self.grid.n_x,
            ny=self.grid.n_y,
            time_stamp=self.grid.time_stamp.to('second').magnitude
        )

        self._cpp_set_geometry_mesh(
            epsilon=epsilon.to('farad/meter').magnitude,
            n2=(epsilon * 0).to('farad/meter').magnitude,  # Non-linear refractive index, if any
            gamma=(epsilon * 0).to('farad/meter').magnitude,  # Non-linear absorption, if any
            sigma_x=sigma_x.to('siemens/meter').magnitude,
            sigma_y=sigma_y.to('siemens/meter').magnitude,
            mu_0=Physics.mu_0.to('henry/meter').magnitude
        )

        self._cpp_set_sources(
            sources=[s for s in self.sources]
        )

        self._cpp_run(Ez_time=self.Ez_t)

        for detector in self.detectors:
            detector.update_data(self.Ez_t)

    @helper.post_mpl_plot
    def plot_frame(
        self,
        frame_number: int,
        enhance_contrast: float = 1,
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
        enhance_contrast : float, optional
            The maximum scale factor for the color limits of the field. Default is 5.
        show_intensity : bool, optional
            If True, displays the intensity instead of the amplitude. Default is False.
        colormap : Optional[Union[str, object]], optional
            The colormap used for visualization. Default is a blue-black-red colormap from the Polytechnique collection.
        """
        figure, ax = plt.subplots(1, 1)
        if show_intensity:
            data = abs(self.Ez_t[frame_number].T)
        else:
            data = self.Ez_t[frame_number].T

        image = ax.pcolormesh(
            self.grid.x_stamp.to('meter').magnitude,
            self.grid.y_stamp.to('meter').magnitude,
            data,
            cmap=colormap
        )

        for component in [*self.components, *self.sources, *self.detectors]:
            component.add_to_ax(ax)

        vmin, vmax = image.get_clim()
        max_diff = max(abs(vmin), abs(vmax)) / enhance_contrast
        image.set_clim([-max_diff, max_diff])

        plt.colorbar(image)

        return figure

    def render_propagation(
        self,
        skip_frame: int = 10,
        enhance_contrast: float = 1,
        auto_adjust_clim: bool = False,
        fps: int = 10,
        save_as: Optional[str] = None,
        show: bool = True,
        colormap: Optional[Union[str, object]] = colormaps.blue_black_red) -> animation.FuncAnimation:
        """
        Render an animation of the field propagation.

        This method sets up the scene, initializes the field display, and creates
        an animation showing the evolution of the field over time.

        Parameters
        ----------
        skip_frame : int, optional
            The number of time steps to skip between frames in the animation. Default is 10.
        enhance_contrast : float, optional
            The maximum scale factor for the color limits of the field amplitude. Default is 1.
        auto_adjust_clim : bool, optional
            If True, automatically adjusts color limits based on field amplitude for each frame. Default is False.
        fps : int, optional
            The frames per second for the animation. Default is 10.
        colormap : Optional[Union[str, object]], optional
            The colormap used for visualizing the data. Default is a predefined blue-black-red colormap.
        save_as : Optional[str], optional
            If provided, saves the animation to the specified file. Default is None.
        show : bool, optional
            If True, displays the animation after rendering. Default is True.

        Returns
        -------
        animation.FuncAnimation
            The animation object that can be displayed or saved.
        """
        figure, ax = plt.subplots(1, 1)

        ax.set(
            xlabel=r'x position [m]',
            ylabel=r'y position [m]',
            aspect='equal'
        )

        ticks_x = ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(x / 1e-6))
        ax.xaxis.set_major_formatter(ticks_x)

        ticks_y = ticker.FuncFormatter(lambda y, pos: '{0:g}'.format(y / 1e-6))
        ax.yaxis.set_major_formatter(ticks_y)


        # Initialize the field display
        initial_field = numpy.zeros(self.Ez_t[0].shape).T
        field_artist = ax.pcolormesh(
            self.grid.x_stamp.to('meter').magnitude,
            self.grid.y_stamp.to('meter').magnitude,
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

        max_amplitude = abs(self.Ez_t).max() / enhance_contrast
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
                max_amplitude = abs(field_t).max() / enhance_contrast
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

        rendered_animation = animation.FuncAnimation(
            fig=figure,
            func=update,
            frames=numpy.arange(0, self.grid.n_steps, skip_frame),
            interval=1000 / fps,
            blit=True,
            init_func=init_func
        )

        if save_as is not None:
            rendered_animation.save(save_as, writer='Pillow', fps=fps)

        if show:
            plt.show()

        return rendered_animation
# -
