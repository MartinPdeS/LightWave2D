#pragma once

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include "../config/config.h"
#include "../field_set/field_set.h"

#define py_ref_rw pybind11::detail::unchecked_mutable_reference
#define py_ref_r pybind11::detail::unchecked_reference

class BaseSource {
public:
    virtual ~BaseSource() {}
    virtual void add_to_field(const Config& config, FieldSet &field_set) = 0;
};

class MultiWavelength : public BaseSource {
public:
    pybind11::array_t<double> omega_list;
    pybind11::array_t<double> amplitude_list;
    pybind11::array_t<double> delay_list;
    pybind11::array_t<ssize_t> indexes;  // Nx2 elements (x, y)

    MultiWavelength(const pybind11::array_t<double>& omega_list, const pybind11::array_t<double>& amplitude_list, const pybind11::array_t<double>& delay_list, const pybind11::array_t<ssize_t>& indexes);

    void add_to_field(const Config& config, FieldSet &field_set) override;
};

class Impulsion : public BaseSource {
public:
    double amplitude;
    double duration;
    double delay;
    pybind11::array_t<ssize_t> indexes;  // Nx2 elements (x, y)

    Impulsion(double amplitude, double duration, double delay, const pybind11::array_t<ssize_t>& indexes);

    void add_to_field(const Config& config, FieldSet &field_set) override;
};
