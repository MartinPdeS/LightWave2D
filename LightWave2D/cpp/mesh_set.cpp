#pragma once

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>

namespace py = pybind11;
#define py_ref_rw py::detail::unchecked_mutable_reference
#define py_ref_r py::detail::unchecked_reference

class MeshSet {
public:
    py::array_t<double> epsilon;
    double mu;
    py::array_t<double> sigma_x;
    py::array_t<double> sigma_y;

    MeshSet(
        const py::array_t<double>& epsilon,
        const double mu,
        const py::array_t<double>& sigma_x,
        const py::array_t<double>& sigma_y):
    epsilon(epsilon), mu(mu), sigma_x(sigma_x), sigma_y(sigma_y)
    {}

    py_ref_r<double, 2> get_epsilon_r() const {
        return epsilon.unchecked<2>();
    }

    py_ref_r<double, 2> get_sigma_x_r() const {
        return sigma_x.unchecked<2>();
    }

    py_ref_r<double, 2> get_sigma_y_r() const {
        return sigma_y.unchecked<2>();
    }

};