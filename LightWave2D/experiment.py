#!/usr/bin/env python
# -*- coding: utf-8 -*-


from typing import Tuple, Optional, Union, List
import logging
import numpy
import matplotlib.animation as animation
from pydantic.dataclasses import dataclass
import matplotlib.pyplot as plt
from MPSPlots import colormaps
from TypedUnit import ureg

from LightWave2D.result import SimulationResult
from LightWave2D.physics import Physics
from LightWave2D.grid import Grid
from LightWave2D import components
from LightWave2D import source
from LightWave2D.detector import PointDetector
from LightWave2D.pml import PML
from LightWave2D.binary import interface_simulator
from LightWave2D.utils import config_dict


LOGGER = logging.getLogger(__name__)


@dataclass(config=config_dict, kw_only=True)
class Experiment(interface_simulator.FDTDSimulator):
    """Class representing an FDTD simulation experiment."""

    grid: Grid
    """The grid of the simulation mesh."""

    def __post_init__(self):
        self.sources = []
        self.components = []
        self.detectors = []
        self.flux_monitors = []
        self.result = None
        self.Ez_t = None
        self.recorded_time_stamp = None
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
        if axis == "x":
            gradient = numpy.diff(field, axis=0) / self.grid.dx
        elif axis == "y":
            gradient = numpy.diff(field, axis=1) / self.grid.dy
        else:
            raise ValueError("Axis must be 'x' or 'y'.")
        return gradient

    def plot(self, *args, **kwargs):
        """Plot the simulation setup; see visualization.plot."""
        from LightWave2D.visualization import plot

        return plot(self, *args, **kwargs)

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
    def add_lens(self, **kwargs) -> components.Lens:
        """
        Add a lens to the simulation.
        """
        return components.Lens(grid=self.grid, **kwargs)

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
    def add_point_pulse(self, **kwargs) -> source.PointPulseSource:
        """
        Add a point pulse source to the simulation.
        """
        return source.PointPulseSource(grid=self.grid, **kwargs)

    @add_to_source
    def add_line_source(self, **kwargs) -> source.LineWaveSource:
        """
        Method to add a source.LineSource to the simulation.
        """
        return source.LineWaveSource(grid=self.grid, **kwargs)

    @add_to_source
    def add_line_pulse(self, **kwargs) -> source.LinePulseSource:
        """
        Add a line pulse source to the simulation.
        """
        return source.LinePulseSource(grid=self.grid, **kwargs)

    @add_to_detector
    def add_point_detector(self, **kwargs) -> PointDetector:
        """
        Method to add a PointDetector to the simulation.
        """
        return PointDetector(grid=self.grid, **kwargs)

    def add_flux_monitor(self, **kwargs):
        """Add an axis-aligned power-flux line; see monitors.FluxMonitor."""
        from LightWave2D.monitors import FluxMonitor

        monitor = FluxMonitor(grid=self.grid, **kwargs)
        self.flux_monitors.append(monitor)
        return monitor

    def get_sigma(self) -> Tuple[numpy.ndarray, numpy.ndarray]:
        """
        Retrieve the sigma values for the PML.

        Returns
        -------
        tuple[numpy.ndarray, numpy.ndarray]
            Conductivity meshes for the x and y directions.
        """
        if self.pml is not None:
            sigma_x, sigma_y = self.pml.sigma_x, self.pml.sigma_y
        else:
            zero_conductivity = ureg.siemens / ureg.meter
            sigma_x = numpy.zeros(self.grid.shape) * zero_conductivity
            sigma_y = numpy.zeros(self.grid.shape) * zero_conductivity

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

    def run(
        self,
        *,
        store_fields: bool = True,
        store_every: int = 1,
        field_every=None,
        detector_every=None,
        field_path=None,
    ) -> SimulationResult:
        """Execute this setup and return a SimulationResult.

        Set store_fields=False for detector/flux-only output. store_every is
        the default cadence; field_every and detector_every override it
        independently. field_path writes fields directly to a new .npy file
        with a coordinate/timestamp sidecar. Existing files are never replaced.
        Legacy Ez_t, recorded_time_stamp and detector.data remain available.
        See execution.run for parameter details.
        """
        from LightWave2D.execution import run

        return run(
            self,
            store_fields=store_fields,
            store_every=store_every,
            field_every=field_every,
            detector_every=detector_every,
            field_path=field_path,
        )

    def _require_field_history(self) -> numpy.ndarray:
        if self.Ez_t is None:
            raise RuntimeError(
                "No field history was stored. Re-run with store_fields=True to plot or render fields."
            )
        return self.Ez_t

    def plot_frame(
        self,
        frame_number: int,
        enhance_contrast: float = 1,
        show_intensity: bool = False,
        colormap: Optional[Union[str, object]] = colormaps.polytechnique.blue_black_red,
    ) -> None:
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
        from LightWave2D import visualization

        self._require_field_history()
        return visualization.plot_frame(
            self.result,
            frame_number=frame_number,
            enhance_contrast=enhance_contrast,
            show_intensity=show_intensity,
            colormap=colormap,
        )

    def render_propagation(
        self,
        skip_frame: int = 10,
        enhance_contrast: float = 1,
        auto_adjust_clim: bool = False,
        fps: int = 10,
        save_as: Optional[str] = None,
        show: bool = True,
        colormap: Optional[Union[str, object]] = colormaps.blue_black_red,
    ) -> animation.FuncAnimation:
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
        from LightWave2D import visualization

        self._require_field_history()
        return visualization.render_propagation(
            self.result,
            skip_frame=skip_frame,
            enhance_contrast=enhance_contrast,
            auto_adjust_clim=auto_adjust_clim,
            fps=fps,
            save_as=save_as,
            show=show,
            colormap=colormap,
        )


# -
