import numpy as np
import pytest
from LightWave2D.utils import bresenham_line


@pytest.mark.parametrize(
    "x0,y0,x1,y1,expected",
    [
        (0, 0, 3, 4, np.array([[0, 1, 1, 2, 3], [0, 1, 2, 3, 4]])),
        (2, 1, 2, 5, np.array([[2, 2, 2, 2, 2], [1, 2, 3, 4, 5]])),
        (0, 0, 3, 0, np.array([[0, 1, 2, 3], [0, 0, 0, 0]])),
    ],
)
def test_bresenham_line_cases(x0, y0, x1, y1, expected):
    """Validate Bresenham line generation for multiple cases."""
    line = bresenham_line(x0, y0, x1, y1)
    assert np.array_equal(line, expected)


if __name__ == "__main__":
    pytest.main(["-W error", "-s", __file__])

