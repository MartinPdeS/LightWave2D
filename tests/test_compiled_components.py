"""Regression tests for the native public component module."""

import numpy as np
import pytest
from TypedUnit import ureg

from LightWave2D import components
from LightWave2D.grid import Grid


@pytest.fixture
def grid():
    return Grid(
        resolution=0.5 * ureg.micrometer,
        size_x=8 * ureg.micrometer,
        size_y=6 * ureg.micrometer,
    )


@pytest.mark.parametrize(
    ("component_class", "arguments"),
    [
        (
            components.Circle,
            {"position": ("center", "center"), "radius": 1 * ureg.micrometer},
        ),
        (
            components.Square,
            {"position": ("center", "center"), "side_length": 2 * ureg.micrometer},
        ),
        (
            components.Ellipse,
            {
                "position": ("center", "center"),
                "width": 2 * ureg.micrometer,
                "height": 1 * ureg.micrometer,
            },
        ),
        (
            components.Triangle,
            {"position": ("center", "center"), "side_length": 2 * ureg.micrometer},
        ),
        (
            components.RingResonator,
            {
                "position": ("center", "center"),
                "inner_radius": 1 * ureg.micrometer,
                "width": 0.5 * ureg.micrometer,
            },
        ),
        (
            components.Lens,
            {
                "position": ("center", "center"),
                "curvature": 3 * ureg.micrometer,
                "width": 2 * ureg.micrometer,
            },
        ),
    ],
)
def test_native_components_create_grid_shaped_masks(grid, component_class, arguments):
    component = component_class(grid=grid, epsilon_r=2.0, **arguments)
    assert component.idx.dtype == bool
    assert component.idx.shape == grid.shape
    assert component.idx.any()


def test_native_waveguide_and_grating_masks(grid):
    waveguide = components.Waveguide(
        grid=grid,
        position_0=("left", "center"),
        position_1=("right", "center"),
        width=0.5 * ureg.micrometer,
        epsilon_r=2.0,
    )
    grating = components.Grating(
        grid=grid,
        position=("left", "center"),
        period=1 * ureg.micrometer,
        duty_cycle=0.5,
        num_periods=3,
        epsilon_r=2.0,
    )
    assert waveguide.idx.any()
    assert grating.idx.any()


def test_native_component_applies_permittivity(grid):
    component = components.Circle(
        grid=grid,
        position=("center", "center"),
        epsilon_r=2.5,
        radius=1 * ureg.micrometer,
    )
    mesh = np.ones(grid.shape)
    component.add_to_epsilon_r_mesh(mesh)
    assert np.all(mesh[component.idx] == 2.5)


def test_native_component_rejects_invalid_dimensions(grid):
    with pytest.raises(ValueError):
        components.Circle(
            grid=grid,
            position=("center", "center"),
            epsilon_r=2.0,
            radius=0 * ureg.micrometer,
        )
