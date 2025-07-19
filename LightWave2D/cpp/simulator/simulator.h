#pragma once

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <omp.h>
#include <vector>
#include <algorithm>
#include <memory>

#include "../source/source.h"
#include "../config/config.h"
#include "../field_set/field_set.h"
#include "../mesh_set/mesh_set.h"

class FDTDSimulator {
public:
    FDTDSimulator(){};

    /// Compute the Yee gradients of the electric field.
    std::tuple<pybind11::array_t<double>, pybind11::array_t<double>>
    compute_yee_gradients(FieldSet& field_set);

    /// Update the magnetic fields Hx and Hy using Maxwell's equations.
    void update_magnetic_fields(FieldSet& field_set);

    /// Compute the Yee gradients of the magnetic fields.
    std::tuple<pybind11::array_t<double>, pybind11::array_t<double>>
    compute_magnetic_field_gradients(FieldSet& field_set);

    /// Apply Kerr nonlinearity to the electric field Ez.
    void apply_kerr_effect(FieldSet& field_set);

    /// Apply Second-Harmonic Generation (SHG) to the electric field Ez.
    void apply_second_harmonic_generation(FieldSet& field_set);

    /// Update the electric field Ez using Maxwell's equations.
    void update_electric_field(FieldSet& field_set);

    /// Apply absorption to the electric field Ez.
    void apply_absorption(FieldSet& field_set);

    /// Update the field data at a specific time step.
    void update_field(pybind11::detail::unchecked_mutable_reference<double, 3>& Ez_time_r, FieldSet& field_set);

    void set_sources(const std::vector<std::shared_ptr<BaseSource>>& sources)
    {
        this->sources = sources;
    }

    void set_config(const double dt, const double dx, const double dy, const size_t nx, const size_t ny, const std::vector<double>& time_stamp)
    {
        this->config = Config(dx, dy, dt, nx, ny, time_stamp);
    }

    void set_geometry_mesh(const pybind11::array_t<double>& epsilon, const pybind11::array_t<double>& n2, const pybind11::array_t<double>& gamma, const pybind11::array_t<double>& sigma_x, const pybind11::array_t<double>& sigma_y, const double mu_0)
    {
        this->mesh_set = MeshSet(epsilon, n2, gamma, mu_0, sigma_x, sigma_y);
    }

    /// Run the full FDTD simulation.
    void run(pybind11::array_t<double> Ez_time);

private:
    Config config;
    MeshSet mesh_set;
    std::vector<std::shared_ptr<BaseSource>> sources;
};
