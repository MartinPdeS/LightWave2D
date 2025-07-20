"""Helper utilities for plotting functions."""

from typing import Callable, Optional, Tuple

import matplotlib.pyplot as plt
from MPSPlots.styles import mps

__all__ = ["plot_helper"]


def plot_helper(func: Callable) -> Callable:
    """Decorator to standardize plotting helper functions.

    Parameters
    ----------
    func : Callable
        The plotting function to decorate. The wrapped function must accept an
        ``ax`` keyword argument.

    Returns
    -------
    Callable
        The wrapped function with automatic axis creation and optional display
        of the resulting figure.
    """

    def wrapper(
        self,
        ax: Optional[plt.Axes] = None,
        show: bool = True,
        figsize: Optional[Tuple[int, int]] = None,
        **kwargs,
    ) -> None:
        """Wrapper injected around the plotting function."""

        if ax is None:
            with plt.style.context(mps):
                _, ax = plt.subplots(1, 1, figsize=figsize)
                ax.set_aspect("equal")
                ax.set(
                    title="Fiber structure",
                    xlabel=r"x-distance [m]",
                    ylabel=r"y-distance [m]",
                )
                ax.ticklabel_format(
                    axis="both", style="sci", scilimits=(-6, -6), useOffset=False
                )

        func(self, ax=ax, **kwargs)

        _, labels = ax.get_legend_handles_labels()

        if labels:
            ax.legend()

        if show:
            plt.show()

    return wrapper
