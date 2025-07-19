#pragma once

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include "../config/config.h"

#define py_ref_rw pybind11::detail::unchecked_mutable_reference
#define py_ref_r pybind11::detail::unchecked_reference



class FieldSet{
public:
    Config config;
    pybind11::array_t<double> Ez;
    pybind11::array_t<double> Hx;
    pybind11::array_t<double> Hy;

    FieldSet(const Config& config);

    void set_to_zero();


    py_ref_r<double, 2> get_Ez_r() {
        return Ez.unchecked<2>();
    }

    py_ref_r<double, 2> get_Hx_r() {
        return Hx.unchecked<2>();
    }

    py_ref_r<double, 2> get_Hy_r() {
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
