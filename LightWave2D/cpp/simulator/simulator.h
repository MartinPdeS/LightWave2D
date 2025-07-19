#pragma once

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <omp.h>
#include <vector>
#include <algorithm>
#include "../source/source.h"
#include "../config/config.h"
#include "../field_set/field_set.h"
#include "../mesh_set/mesh_set.h"

#define py_ref_rw pybind11::detail::unchecked_mutable_reference
#define py_ref_r pybind11::detail::unchecked_reference


/**
 * @brief Compute the Yee gradients of the electric field.
 *
 * @param config Configuration containing simulation parameters.
 * @param field_set FieldSet object containing the field data.
 * @return A tuple of arrays (dEz_dx, dEz_dy) representing the gradients.
 */
std::tuple<pybind11::array_t<double>, pybind11::array_t<double>> compute_yee_gradients(const Config &config, FieldSet& field_set);

/**
 * @brief Update the magnetic fields Hx and Hy using Maxwell's equations.
 *
 * @param config Configuration containing simulation parameters.
 * @param mesh_set MeshSet object containing mesh data.
 * @param field_set FieldSet object containing the field data.
 */
void update_magnetic_fields(const Config& config, const MeshSet& mesh_set, FieldSet& field_set);

/**
 * @brief Compute the Yee gradients of the magnetic fields.
 *
 * @param config Configuration containing simulation parameters.
 * @param field_set FieldSet object containing the field data.
 * @return A tuple of arrays (dHy_dx, dHx_dy) representing the gradients.
 */
std::tuple<pybind11::array_t<double>, pybind11::array_t<double>> compute_magnetic_field_gradients(const Config &config, FieldSet& field_set);

/**
 * @brief Apply Kerr nonlinearity to the electric field Ez.
 *
 * @param config Configuration containing simulation parameters.
 * @param field_set FieldSet object containing the field data.
 * @param mesh_set MeshSet object containing mesh data.
 */
void apply_kerr_effect(const Config &config, FieldSet& field_set, MeshSet& mesh_set);

/**
 * @brief Apply Second-Harmonic Generation (SHG) to the electric field Ez.
 *
 * @param config Configuration containing simulation parameters.
 * @param field_set FieldSet object containing the field data.
 * @param mesh_set MeshSet object containing mesh data.
 */
void apply_second_harmonic_generation(const Config &config, FieldSet& field_set, MeshSet& mesh_set);

/**
 * @brief Update the electric field Ez using Maxwell's equations.
 *
 * @param config Configuration containing simulation parameters.
 * @param field_set FieldSet object containing the field data.
 * @param mesh_set MeshSet object containing mesh data.
 */
void update_electric_field(const Config &config, FieldSet& field_set, MeshSet& mesh_set);

/**
 * @brief Apply absorption to the electric field Ez.
 *
 * @param config Configuration containing simulation parameters.
 * @param field_set FieldSet object containing the field data.
 * @param mesh_set MeshSet object containing mesh data.
 */
void apply_absorption(const Config &config, FieldSet &field_set, MeshSet &mesh_set);

/**
 * @brief Update the field data at a specific time step.
 *
 * @param config Configuration containing simulation parameters.
 * @param Ez_time_r Reference to the 3D array holding the time evolution of Ez.
 * @param field_set FieldSet object containing the field data.
 */
void update_field(const Config &config, py_ref_rw<double, 3>& Ez_time_r, FieldSet& field_set);


/**
 * @brief Run the FDTD simulation.
 *
 * @param Ez_time 3D array to store the electric field over time.
 * @param time_stamp Vector of time stamps for the simulation.
 * @param sigma_x The conductivity in the x direction.
 * @param sigma_y The conductivity in the y direction.
 * @param epsilon The permittivity of the grid.
 * @param dt The time step.
 * @param mu_0 The permeability of free space.
 * @param n_steps The number of simulation steps.
 * @param dx The grid spacing in the x direction.
 * @param dy The grid spacing in the y direction.
 * @param nx The number of grid points in the x direction.
 * @param ny The number of grid points in the y direction.
 * @param sources Vector of sources in the simulation.
 */
void run_fdtd(
    pybind11::array_t<double> Ez_time,
    const std::vector<double>& time_stamp,
    const pybind11::array_t<double>& sigma_x,
    const pybind11::array_t<double>& sigma_y,
    const pybind11::array_t<double>& epsilon,
    const pybind11::array_t<double>& gamma,
    const pybind11::array_t<double>& n2,
    const double dt,
    const double mu_0,
    const size_t n_steps,
    const double dx,
    const double dy,
    const size_t nx,
    const size_t ny,
    std::vector<std::shared_ptr<BaseSource>>& sources
    );
