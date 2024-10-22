from typing import Optional, Tuple
from MPSPlots.styles import mps
import matplotlib.pyplot as plt


def _plot_helper(function):
    def wrapper(self, ax: plt.Axes = None, show: bool = True, figsize: Optional[Tuple[int, int]] = None, **kwargs):
        if ax is None:
            with plt.style.context(mps):
                _, ax = plt.subplots(1, 1)
                ax.set_aspect('equal')
                ax.set(title='Fiber structure', xlabel=r'x-distance [m]', ylabel=r'y-distance [m]')
                ax.ticklabel_format(axis='both', style='sci', scilimits=(-6, -6), useOffset=False)

        function(self, ax=ax, **kwargs)

        _, labels = ax.get_legend_handles_labels()

        # Only add a legend if there are labels
        if labels:
            ax.legend()

        if show:
            plt.show()

    return wrapper
