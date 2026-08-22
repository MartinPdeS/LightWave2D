#pragma once

#include <cstdint>

#include <pybind11/pybind11.h>

/**
 * @brief Samples the electric field at one grid cell over simulation time.
 *
 * The detector keeps the most recently sampled data and matching timestamps,
 * and provides lightweight Matplotlib drawing helpers for the public API.
 */
class PointDetector {
public:
    /** @brief Construct a detector at a physical or named grid position. */
    PointDetector(pybind11::object grid, pybind11::tuple position, bool coherent = true, pybind11::object facecolor = pybind11::str("green"), pybind11::object edgecolor = pybind11::str("green"), double alpha = 0.8, double rotation = 0.0);

    /** @brief Extract coherent or magnitude-only samples from a field history. */
    void update_data(pybind11::object field, pybind11::object time_stamp);
    void add_to_ax(const pybind11::object& axis) const;
    void plot() const;
    void plot_data() const;

    pybind11::object grid, p0, data, time_stamp, facecolor, edgecolor;
    bool coherent;
    double alpha, rotation;
};
