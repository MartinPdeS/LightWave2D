#pragma once

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include "config.cpp"

namespace py = pybind11;
#define py_ref_rw py::detail::unchecked_mutable_reference
#define py_ref_r py::detail::unchecked_reference



class FieldSet{
public:
    Config config;
    py::array_t<double> Ez;
    py::array_t<double> Hx;
    py::array_t<double> Hy;

    FieldSet(const Config& config) : config(config)
    {
        Hx = py::array_t<double>({config.nx, config.ny});
        Hy = py::array_t<double>({config.nx, config.ny});
        Ez = py::array_t<double>({config.nx, config.ny});
        this->set_to_zero();
    }


    void set_to_zero() {
        py_ref_rw<double, 2>
            Ez_r = Ez.mutable_unchecked<2>(),
            Hx_r = Hx.mutable_unchecked<2>(),
            Hy_r = Hy.mutable_unchecked<2>();

        for (ssize_t i = 0; i < config.nx; ++i) {
            for (ssize_t j = 0; j < config.ny; ++j) {
                Ez_r(i, j) = 0.0;
                Hx_r(i, j) = 0.0;
                Hy_r(i, j) = 0.0;
            }
        }
    }


    py_ref_r<double, 2> get_Ez_r() const {
        return Ez.unchecked<2>();
    }

    py_ref_r<double, 2> get_Hx_r() const {
        return Hx.unchecked<2>();
    }

    py_ref_r<double, 2> get_Hy_r() const {
        return Hy.unchecked<2>();
    }

    py_ref_rw<double, 2> get_Ez_rw() {
        return Ez.mutable_unchecked<2>();
    }

    py_ref_rw<double, 2> get_Hx_rw() {
        return Hx.mutable_unchecked<2>();
    }

    py_ref_rw<double, 2> get_Hy_rw() {
        return Hy.mutable_unchecked<2>();
    }

};

