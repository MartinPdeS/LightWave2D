#pragma once

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>

namespace py = pybind11;
#define py_ref_rw pybind11::detail::unchecked_mutable_reference
#define py_ref_r pybind11::detail::unchecked_reference

class MeshSet {
public:
    pybind11::array_t<double> epsilon;
    pybind11::array_t<double> n2;
    pybind11::array_t<double> gamma;
    double mu;
    pybind11::array_t<double> sigma_x;
    pybind11::array_t<double> sigma_y;

    MeshSet() = default;

    MeshSet(
        const pybind11::array_t<double>& epsilon,
        const pybind11::array_t<double>& n2,
        const pybind11::array_t<double>& gamma,
        const double mu,
        const pybind11::array_t<double>& sigma_x,
        const pybind11::array_t<double>& sigma_y);


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