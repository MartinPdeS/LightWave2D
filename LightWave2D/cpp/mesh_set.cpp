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
    py::array_t<double> n2;
    py::array_t<double> gamma;
    double mu;
    py::array_t<double> sigma_x;
    py::array_t<double> sigma_y;

    MeshSet(
        const py::array_t<double>& epsilon,
        const py::array_t<double>& n2,
        const py::array_t<double>& gamma,
        const double mu,
        const py::array_t<double>& sigma_x,
        const py::array_t<double>& sigma_y):
    epsilon(epsilon), n2(n2), gamma(gamma), mu(mu), sigma_x(sigma_x), sigma_y(sigma_y)
    {}


    py_ref_r<double, 2> get_gamma_r() const {
        return gamma.unchecked<2>();
    }
    py_ref_r<double, 2> get_n2_r() const {
        return n2.unchecked<2>();
    }

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