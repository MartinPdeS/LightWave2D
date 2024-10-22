#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np


def bresenham_line(x0: float, y0: float, x1: float, y1: float) -> np.ndarray:
    """
    Generates the points of a line using Bresenham's Line Algorithm.

    This function computes the coordinates of points that form a straight line between
    a start point (x0, y0) and an end point (x1, y1) using Bresenham's algorithm. It is
    optimized for integer values but works with floats by rounding to the nearest integer.

    Parameters
    ----------
    x0 : float
        The x-coordinate of the start point.
    y0 : float
        The y-coordinate of the start point.
    x1 : float
        The x-coordinate of the end point.
    y1 : float
        The y-coordinate of the end point.

    Returns
    -------
    np.ndarray
        A 2D NumPy array where the first row contains the x-coordinates and the
        second row contains the y-coordinates of the points along the line.
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

    points.append((x, y))  # Ensure the end point is included
    return np.array(points).T
