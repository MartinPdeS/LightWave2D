#pragma once

#include <cstdint>

#include <pybind11/pybind11.h>

/**
 * @brief Perfectly matched layer conductivity profile for FDTD boundaries.
 *
 * Conductivity rises polynomially from the interior edge to each outer grid
 * boundary and is retained as unit-bearing conductivity arrays.
 */
class PML {
public:
    /** @brief Construct conductivity profiles for the supplied grid. */
    PML(pybind11::object grid, pybind11::object width, pybind11::object sigma_max, int order = 3);
    /** @brief Add the combined conductivity profile to a Matplotlib axis. */
    void add_to_ax(const pybind11::object& axis) const;
    void plot(int unit_size = 6) const;

    pybind11::object grid, width, sigma_max, sigma_x, sigma_y, width_start, width_stop;
    int order;
};
