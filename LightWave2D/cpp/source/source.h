#pragma once

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include <array>
#include "../config/config.h"
#include "../field_set/field_set.h"

#define py_ref_rw pybind11::detail::unchecked_mutable_reference
#define py_ref_r pybind11::detail::unchecked_reference

/** @brief Abstract time-dependent source injected into an FDTD field set. */
class BaseSource {
public:
    virtual ~BaseSource() {}
    virtual void add_to_field(const Config& config, FieldSet &field_set) = 0;
};

/** @brief Discrete grid indexes occupied by a source geometry. */
class SourceGeometry {
public:
    virtual ~SourceGeometry() = default;
    const std::vector<std::array<int64_t, 2>>& indexes() const { return indexes_; }

protected:
    std::vector<std::array<int64_t, 2>> indexes_;
};

/** @brief One-cell source geometry. */
class PointGeometry final : public SourceGeometry {
public:
    PointGeometry(int64_t x_index, int64_t y_index);
};

/** @brief Bresenham-rasterized line source geometry. */
class LineGeometry final : public SourceGeometry {
public:
    LineGeometry(int64_t x0, int64_t y0, int64_t x1, int64_t y1);
};

/** @brief Superposition of delayed monochromatic source terms. */
class MultiWavelength : public BaseSource {
public:
    pybind11::array_t<double> omega_list;      // List of angular frequencies (in radians per second)
    pybind11::array_t<double> amplitude_list;  // List of amplitudes for each frequency
    pybind11::array_t<double> delay_list;      // List of delays for each frequency
    pybind11::array_t<int64_t> indexes;        // Nx2 elements (x, y)

    /**
     * MultiWavelength source constructor
     * @param omega_list: List of angular frequencies (in radians per second)
     * @param amplitude_list: List of amplitudes for each frequency
     * @param delay_list: List of delays for each frequency
     * @param indexes: Array of shape (N, 2) containing the x and y coordinates of the source points
     */
    MultiWavelength(const pybind11::array_t<double>& omega_list, const pybind11::array_t<double>& amplitude_list, const pybind11::array_t<double>& delay_list, const pybind11::array_t<int64_t>& indexes);

    /**
     * Add the multi-wavelength source to the electric field Ez
     * @param config: Configuration object containing simulation parameters
     * @param field_set: FieldSet object containing the field data
     */
    void add_to_field(const Config& config, FieldSet &field_set) override;
};

/** @brief Temporally localized pulse source. */
class Pulse : public BaseSource {
public:
    double amplitude;
    double duration;
    double delay;
    pybind11::array_t<int64_t> indexes;  // Nx2 elements (x, y)

    /**
     * Pulse source constructor
     * @param amplitude: Amplitude of the pulse
     * @param duration: Duration of the pulse
     * @param delay: Delay before the pulse starts
     * @param indexes: Array of shape (N, 2) containing the x and y coordinates of the source points
     */

    Pulse(const double amplitude, const double duration, const double delay, const pybind11::array_t<int64_t>& indexes);

    /**
     * Add the pulse source to the electric field Ez
     * @param config: Configuration object containing simulation parameters
     * @param field_set: FieldSet object containing the field data
     */
    void add_to_field(const Config& config, FieldSet &field_set) override;
};
