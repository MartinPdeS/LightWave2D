import numpy as np
from LightWave2D.utils import bresenham_line


def test_bresenham_basic():
    line = bresenham_line(0, 0, 3, 4)
    expected = np.array([[0, 1, 1, 2, 3], [0, 1, 2, 3, 4]])
    assert np.array_equal(line, expected)

