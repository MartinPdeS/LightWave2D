import numpy
import matplotlib.pyplot as plt
import time
from MPSPlots.colormaps import blue_black_red
from LightWave2D.grid import Grid


def plot_slice(*fields, absolute: bool, slc=None):
    n_ax = len(fields)
    figure, axes = plt.subplots(1, n_ax, figsize=(5 * n_ax, 3))

    axes = numpy.atleast_1d(axes)

    for ax, field in zip(axes, fields):
        if absolute:
            field = abs(field)

        if slc is not None:
            field = field[slc]
        image = ax.imshow(field)
        plt.colorbar(mappable=image)
        ax.axis('off')

    plt.show()


def plot_propgation(field: numpy.ndarray, n_step: int, grid: Grid):
    plt.ion()
    figure, ax = plt.subplots(1, 1)
    ax.set_title('FDTD Simulation at time step')
    ax.set_xlabel('x position (m)')
    ax.set_ylabel('y position (m)')
    plt.axis('off')

    mappable = ax.imshow(
        numpy.zeros(field[0].T.shape),
        origin='lower',
        cmap=blue_black_red
    )

    for t in range(grid.n_steps):
        field_t = field[t].T
        if t % n_step == 0:
            mappable.set_data(field_t)
            mappable.set_clim(vmin=-1, vmax=+1)
            figure.canvas.draw()
            figure.canvas.flush_events()
            time.sleep(0.1)
            ax.grid(False)

            plt.show()


def bresenham_line(x0, y0, x1, y1):
    """
    Bresenham's Line Algorithm
    Produces a list of tuples from start and end

    :param x0: x-coordinate of the start point
    :param y0: y-coordinate of the start point
    :param x1: x-coordinate of the end point
    :param y1: y-coordinate of the end point
    :return: Numpy array of points (x, y) along the line
    """
    points = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    x, y = x0, y0
    sx = -1 if x0 > x1 else 1
    sy = -1 if y0 > y1 else 1

    if dx > dy:
        err = dx / 2.0
        while x != x1:
            points.append((x, y))
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
    else:
        err = dy / 2.0
        while y != y1:
            points.append((x, y))
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy

    points.append((x, y))  # Make sure the end point is included
    return numpy.array(points).T
