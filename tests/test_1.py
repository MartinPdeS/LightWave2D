import numpy as np

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
    return np.array(points)

# Example usage
x0, y0 = 0, 3  # Start point
x1, y1 = 6, 4  # End point
line_points = bresenham_line(0, 0, 20, 20)
print(line_points)