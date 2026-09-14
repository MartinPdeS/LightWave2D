"""Matplotlib views for experiment geometry and stored simulation results."""

from typing import Optional, Union, List
import logging
import numpy
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.ticker as ticker
from MPSPlots import colormaps
from LightWave2D.helper import plot_helper

LOGGER = logging.getLogger(__name__)


@plot_helper
def plot(
    self,
    ax: plt.Axes,
) -> None:
    """
    Generates a plot of the FDTD simulation setup using a specified colormap.

    This function initializes a plotting scene and adds elements of the FDTD simulation
    such as components, sources, detectors, and optionally the PML layers. It adjusts
    the axis properties and attaches a colorbar based on the selected colormap.

    """
    # Add PML layers to the plot if present
    if self.pml:
        LOGGER.debug("Plotting PML: grid=%s", self.grid.shape)
        self.pml.add_to_ax(ax)

    for component in [
        *self.components,
        *self.sources,
        *self.detectors,
        *getattr(self, "flux_monitors", ()),
    ]:
        LOGGER.debug("Plotting %s", type(component).__name__)
        component.add_to_ax(ax)

    ax.legend()
    ax.autoscale_view()


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
    field_history = self._require_field_history()
    figure, ax = plt.subplots(1, 1)
    if show_intensity:
        data = abs(field_history[frame_number].T)
    else:
        data = field_history[frame_number].T

    image = ax.pcolormesh(
        self.grid.x_stamp.to("meter").magnitude,
        self.grid.y_stamp.to("meter").magnitude,
        data,
        cmap=colormap,
    )

    for component in [
        *self.components,
        *self.sources,
        *self.detectors,
        *getattr(self, "flux_monitors", ()),
    ]:
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
    field_history = self._require_field_history()
    if not isinstance(skip_frame, int) or skip_frame < 1:
        raise ValueError("skip_frame must be a positive integer.")
    if not isinstance(fps, (int, float)) or fps <= 0:
        raise ValueError("fps must be positive.")
    if field_history.shape[0] == 0:
        raise RuntimeError("Cannot render an empty field history.")
    frame_indexes = numpy.arange(0, len(field_history), skip_frame)
    LOGGER.debug(
        "Rendering %d frames from %d stored fields (skip_frame=%d, fps=%s)",
        frame_indexes.size,
        len(field_history),
        skip_frame,
        fps,
    )
    figure, ax = plt.subplots(1, 1)

    ax.set(xlabel=r"x position [m]", ylabel=r"y position [m]", aspect="equal")

    ticks_x = ticker.FuncFormatter(lambda x, pos: "{0:g}".format(x / 1e-6))
    ax.xaxis.set_major_formatter(ticks_x)

    ticks_y = ticker.FuncFormatter(lambda y, pos: "{0:g}".format(y / 1e-6))
    ax.yaxis.set_major_formatter(ticks_y)

    # Initialize the field display
    initial_field = numpy.zeros(field_history[0].shape).T
    field_artist = ax.pcolormesh(
        self.grid.x_stamp.to("meter").magnitude,
        self.grid.y_stamp.to("meter").magnitude,
        initial_field,
        cmap=colormap,
    )

    title = ax.text(
        x=0.85, y=0.9, s="", transform=ax.transAxes, ha="center", color="white"
    )

    # Store all artists for updating
    artist_list = [field_artist]

    # Add other components to the axis and their artists to the list
    for component in self.components:
        artist_list.append(component.add_to_ax(ax))

    max_amplitude = (
        max(float(numpy.max(numpy.abs(frame))) for frame in field_history)
        / enhance_contrast
    )
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
        time = self.recorded_time_stamp[frame]
        field_t = field_history[frame].T
        field_artist.set_array(field_t)

        if auto_adjust_clim:
            max_amplitude = abs(field_t).max() / enhance_contrast
            field_artist.set_clim(vmin=-max_amplitude, vmax=max_amplitude)

        title.set_text(f"time: {time:.1e}")

        return (
            *artist_list,
            title,
        )

    def init_func():
        """
        Initialization function for the animation; called at the start.

        Returns
        -------
        Tuple
            A tuple containing the initial field artist and title.
        """
        time = 0
        title.set_text(f"time: {time:.1e}")
        ax.set_xticks([])
        ax.set_yticks([])
        return (
            field_artist,
            title,
        )

    rendered_animation = animation.FuncAnimation(
        fig=figure,
        func=update,
        frames=frame_indexes,
        interval=1000 / fps,
        blit=True,
        init_func=init_func,
    )

    if save_as is not None:
        rendered_animation.save(save_as, writer="pillow", fps=fps)

    if show:
        plt.show()

    return rendered_animation
