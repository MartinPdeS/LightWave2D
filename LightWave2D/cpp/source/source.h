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
    pybind11::array_t<double> omega_list;      // List of angular frequencies (in radians per second)
    pybind11::array_t<double> amplitude_list;  // List of amplitudes for each frequency
    pybind11::array_t<double> delay_list;      // List of delays for each frequency
    pybind11::array_t<ssize_t> indexes;        // Nx2 elements (x, y)

    /**
     * MultiWavelength source constructor
     * @param omega_list: List of angular frequencies (in radians per second)
     * @param amplitude_list: List of amplitudes for each frequency
     * @param delay_list: List of delays for each frequency
     * @param indexes: Array of shape (N, 2) containing the x and y coordinates of the source points
     */
    MultiWavelength(const pybind11::array_t<double>& omega_list, const pybind11::array_t<double>& amplitude_list, const pybind11::array_t<double>& delay_list, const pybind11::array_t<ssize_t>& indexes);

    /**
     * Add the multi-wavelength source to the electric field Ez
     * @param config: Configuration object containing simulation parameters
     * @param field_set: FieldSet object containing the field data
     */
    void add_to_field(const Config& config, FieldSet &field_set) override;
};

class Impulsion : public BaseSource {
public:
    double amplitude;
    double duration;
    double delay;
    pybind11::array_t<ssize_t> indexes;  // Nx2 elements (x, y)

    /**
     * Impulsion source constructor
     * @param amplitude: Amplitude of the impulsion
     * @param duration: Duration of the impulsion
     * @param delay: Delay before the impulsion starts
     * @param indexes: Array of shape (N, 2) containing the x and y coordinates of the source points
     */

    Impulsion(const double amplitude, const double duration, const double delay, const pybind11::array_t<ssize_t>& indexes);

    /**
     * Add the impulsion source to the electric field Ez
     * @param config: Configuration object containing simulation parameters
     * @param field_set: FieldSet object containing the field data
     */
    void add_to_field(const Config& config, FieldSet &field_set) override;
};
