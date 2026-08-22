#pragma once

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>

#define py_ref pybind11::detail::unchecked_mutable_reference

/**
 * @brief Immutable-at-run-start numerical configuration for the FDTD solver.
 *
 * Stores SI spacings, dimensions, time samples, and the current iteration.
 */
class Config {
public:
    double dx;
    double dy;
    double dt;
    int64_t nx;
    int64_t ny;
    std::vector<double> time_stamp;
    int64_t iteration = 0;
    double time = 0;

    Config() = default;

    Config(
        const double dx,
        const double dy,
        const double dt,
        const int64_t nx,
        const int64_t ny,
        const std::vector<double>& time_stamp)
    : dx(dx), dy(dy), dt(dt), nx(nx), ny(ny), time_stamp(time_stamp)
    {}

    /** @brief Advance to the next available time sample. */
    void next()
    {
        if (iteration + 1 < static_cast<int64_t>(time_stamp.size())) {
            iteration += 1;
            time = time_stamp[iteration];
        }
    }


};
