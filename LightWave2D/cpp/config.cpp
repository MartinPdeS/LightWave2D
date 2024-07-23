#pragma once

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>


namespace py = pybind11;
#define py_ref py::detail::unchecked_mutable_reference

class Config {
public:
    double dx;
    double dy;
    double dt;
    ssize_t nx;
    ssize_t ny;
    std::vector<double> time_stamp;
    ssize_t iteration = 0;
    double time = 0;

    Config(
        const double dx,
        const double dy,
        const double dt,
        const double nx,
        const double ny,
        const std::vector<double>& time_stamp)
    : dx(dx), dy(dy), dt(dt), nx(nx), ny(ny), time_stamp(time_stamp)
    {}

    void next()
    {
        iteration += 1;
        time = time_stamp[iteration];
    }


};
