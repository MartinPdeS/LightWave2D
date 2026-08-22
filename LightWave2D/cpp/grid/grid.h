#pragma once

#include <cstdint>

#include <pybind11/pybind11.h>

/**
 * @brief Unit-aware Cartesian grid used by a two-dimensional FDTD simulation.
 *
 * The class owns the cell-aligned spatial and temporal coordinates exposed to
 * Python. Length-valued arguments and public coordinate arrays retain their
 * Pint units at the binding boundary.
 */
class Grid {
public:
    /** @brief Construct a grid from spatial resolution, extents, and step count. */
    Grid(pybind11::object resolution, pybind11::object size_x, pybind11::object size_y, int64_t n_steps = 200);

    /** @brief Return Euclidean distances from the supplied physical point. */
    pybind11::object get_distance_grid(pybind11::object x0, pybind11::object y0) const;
    /** @brief Resolve physical or named coordinates and return their cell indexes. */
    pybind11::object get_coordinate(pybind11::object x, pybind11::object y) const;
    pybind11::object parse_x_position(pybind11::object value) const;
    pybind11::object parse_y_position(pybind11::object value) const;

    /** @brief Python-facing unit-bearing grid metadata and coordinate arrays. */
    pybind11::object resolution, size_x, size_y, dx, dy, dt, time_stamp, x_stamp, y_stamp, x_mesh, y_mesh, polygon, shape;
    int64_t n_x, n_y, n_steps;

private:
    pybind11::object ureg_;
    double meter_value(const pybind11::object& value) const;
    pybind11::object meter_quantity(double value) const;
    pybind11::object parse_position(pybind11::object value, bool is_x) const;
};
