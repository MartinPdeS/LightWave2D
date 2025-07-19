#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <omp.h>
#include <vector>
#include <algorithm>
#include "source.cpp"
#include "config.cpp"
#include "field_set.cpp"
#include "mesh_set.cpp"

namespace py = pybind11;
#define py_ref_rw py::detail::unchecked_mutable_reference
#define py_ref_r py::detail::unchecked_reference


/**
 * @brief Compute the Yee gradients of the electric field.
 *
 * @param config Configuration containing simulation parameters.
 * @param field_set FieldSet object containing the field data.
 * @return A tuple of arrays (dEz_dx, dEz_dy) representing the gradients.
 */
std::tuple<py::array_t<double>, py::array_t<double>> compute_yee_gradients(const Config &config, FieldSet& field_set)
{
    // Initialize gradient arrays
    py::array_t<double> dEz_dx({config.nx - 1, config.ny});
    py::array_t<double> dEz_dy({config.nx, config.ny - 1});

    // Get references to the gradient arrays and the electric field
    py_ref_rw<double, 2>
        dEz_dx_r = dEz_dx.mutable_unchecked<2>(),
        dEz_dy_r = dEz_dy.mutable_unchecked<2>();
    py_ref_r<double, 2> Ez_r = field_set.get_Ez_r();


    // Compute the gradients
    #pragma omp parallel for collapse(2)
    for (ssize_t i = 0; i < config.nx - 1; ++i)
        for (ssize_t j = 0; j < config.ny; ++j)
            dEz_dx_r(i, j) = (Ez_r(i + 1, j) - Ez_r(i, j)) / config.dx;

    #pragma omp parallel for collapse(2)
    for (ssize_t i = 1; i < config.nx; ++i)
        for (ssize_t j = 0; j < config.ny - 1; ++j)
            dEz_dy_r(i, j) = (Ez_r(i, j + 1) - Ez_r(i, j)) / config.dy;

    return std::make_tuple(dEz_dx, dEz_dy);
}

/**
 * @brief Update the magnetic fields Hx and Hy using Maxwell's equations.
 *
 * @param config Configuration containing simulation parameters.
 * @param mesh_set MeshSet object containing mesh data.
 * @param field_set FieldSet object containing the field data.
 */
void update_magnetic_fields(const Config& config, const MeshSet& mesh_set, FieldSet& field_set)
{
    // Compute Yee gradients of the electric field
    auto [dEz_dx, dEz_dy] = compute_yee_gradients(config, field_set);

    // Get references to arrays
    py_ref_r<double, 2>
        dEz_dx_r = dEz_dx.unchecked<2>(),
        dEz_dy_r = dEz_dy.unchecked<2>(),
        sigma_x_r = mesh_set.get_sigma_x_r(),
        sigma_y_r = mesh_set.get_sigma_y_r();

    py_ref_rw<double, 2>
        Hx_rw = field_set.get_Hx_rw(),
        Hy_rw = field_set.get_Hy_rw();

    // Update Hx
    #pragma omp parallel for collapse(2)
    for (ssize_t i = 0; i < config.nx; ++i)
        for (ssize_t j = 0; j < config.ny - 1; ++j)
            Hx_rw(i, j) -= (config.dt / mesh_set.mu) * dEz_dy_r(i, j) * (1 - sigma_y_r(i, j) * (config.dt / mesh_set.mu) / 2);

    // Update Hy
    #pragma omp parallel for collapse(2)
    for (ssize_t i = 0; i < config.nx - 1; ++i)
        for (ssize_t j = 0; j < config.ny; ++j)
            Hy_rw(i, j) += (config.dt / mesh_set.mu) * dEz_dx_r(i, j) * (1 - sigma_x_r(i, j) * (config.dt / mesh_set.mu) / 2);
}

/**
 * @brief Compute the Yee gradients of the magnetic fields.
 *
 * @param config Configuration containing simulation parameters.
 * @param field_set FieldSet object containing the field data.
 * @return A tuple of arrays (dHy_dx, dHx_dy) representing the gradients.
 */
std::tuple<py::array_t<double>, py::array_t<double>> compute_magnetic_field_gradients(const Config &config, FieldSet& field_set)
{
    // Initialize gradient arrays
    py::array_t<double> dHy_dx({config.nx - 1, config.ny - 1});
    py::array_t<double> dHx_dy({config.nx - 1, config.ny - 1});

    // Get mutable references to the gradient arrays
    py_ref_rw<double, 2>
        dHy_dx_rw = dHy_dx.mutable_unchecked<2>(),
        dHx_dy_rw = dHx_dy.mutable_unchecked<2>();

    // Get read-only references to the magnetic fields
    py_ref_r<double, 2>
        Hx_r = field_set.get_Hx_rw(),
        Hy_r = field_set.get_Hy_rw();

    // Compute the gradients
    #pragma omp parallel for collapse(2)
    for (ssize_t i = 1; i < config.nx - 1; ++i)
        for (ssize_t j = 1; j < config.ny - 1; ++j)
            dHy_dx_rw(i, j) = (Hy_r(i, j) - Hy_r(i - 1, j)) / config.dx;

    #pragma omp parallel for collapse(2)
    for (ssize_t i = 1; i < config.nx - 1; ++i)
        for (ssize_t j = 1; j < config.ny - 1; ++j)
            dHx_dy_rw(i, j) = (Hx_r(i, j) - Hx_r(i, j - 1)) / config.dy;

    return std::make_tuple(dHy_dx, dHx_dy);
}

/**
 * @brief Apply Kerr nonlinearity to the electric field Ez.
 *
 * @param config Configuration containing simulation parameters.
 * @param field_set FieldSet object containing the field data.
 * @param mesh_set MeshSet object containing mesh data.
 */
void apply_kerr_effect(const Config &config, FieldSet& field_set, MeshSet& mesh_set)
{
    // Get mutable references to the z electric field
    py_ref_rw<double, 2> Ez_rw = field_set.get_Ez_rw();

    // Get read-only references to the permittivity
    py_ref_r<double, 2> epsilon_r = mesh_set.get_epsilon_r();
    py_ref_r<double, 2> n2_r = mesh_set.get_n2_r();

    // Apply Kerr effect
    #pragma omp parallel for collapse(2)
    for (ssize_t i = 1; i < config.nx - 1; ++i) {
        for (ssize_t j = 1; j < config.ny - 1; ++j) {
            double intensity = Ez_rw(i, j) * Ez_rw(i, j);
            double nonlinear_epsilon = epsilon_r(i, j) + n2_r(i, j) * intensity;
            Ez_rw(i, j) *= (config.dt / nonlinear_epsilon);
        }
    }
}

/**
 * @brief Apply Second-Harmonic Generation (SHG) to the electric field Ez.
 *
 * @param config Configuration containing simulation parameters.
 * @param field_set FieldSet object containing the field data.
 * @param mesh_set MeshSet object containing mesh data.
 */
void apply_second_harmonic_generation(const Config &config, FieldSet& field_set, MeshSet& mesh_set)
{
    // Get mutable references to the z electric field
    py_ref_rw<double, 2> Ez_rw = field_set.get_Ez_rw();
    py_ref_r<double, 2> gamma_r = mesh_set.get_gamma_r();

    // Apply Second-Harmonic Generation (SHG)
    #pragma omp parallel for collapse(2)
    for (ssize_t i = 0; i < config.nx; ++i) {
        for (ssize_t j = 0; j < config.ny; ++j) {
            double intensity = Ez_rw(i, j) * Ez_rw(i, j);
            Ez_rw(i, j) += gamma_r(i, j) * intensity * config.dt;
        }
    }
}

/**
 * @brief Update the electric field Ez using Maxwell's equations.
 *
 * @param config Configuration containing simulation parameters.
 * @param field_set FieldSet object containing the field data.
 * @param mesh_set MeshSet object containing mesh data.
 */
void update_electric_field(const Config &config, FieldSet& field_set, MeshSet& mesh_set)
{
    // Compute the Yee gradients of the magnetic fields Hx and Hy
    auto [dHy_dx, dHx_dy] = compute_magnetic_field_gradients(config, field_set);

    // Get mutable references to the z electric field
    py_ref_rw<double, 2> Ez_rw = field_set.get_Ez_rw();

    // Get read-only references to the magnetic fields gradients
    py_ref_r<double, 2>
        dHy_dx_r = dHy_dx.unchecked<2>(),
        dHx_dy_r = dHx_dy.unchecked<2>(),
        epsilon_r = mesh_set.get_epsilon_r();

    // Update Ez
    #pragma omp parallel for collapse(2)
    for (ssize_t i = 1; i < config.nx - 1; ++i)
        for (ssize_t j = 1; j < config.ny - 1; ++j)
            Ez_rw(i, j) += (config.dt / epsilon_r(i, j)) * (dHy_dx_r(i, j) - dHx_dy_r(i, j));
}

/**
 * @brief Apply absorption to the electric field Ez.
 *
 * @param config Configuration containing simulation parameters.
 * @param field_set FieldSet object containing the field data.
 * @param mesh_set MeshSet object containing mesh data.
 */
void apply_absorption(const Config &config, FieldSet &field_set, MeshSet &mesh_set) {
    // Get references to arrays
    py_ref_rw<double, 2> Ez_rw = field_set.get_Ez_rw();

    py_ref_r<double, 2>
        sigma_x_r = mesh_set.sigma_x.unchecked<2>(),
        sigma_y_r = mesh_set.sigma_y.unchecked<2>(),
        epsilon_r = mesh_set.get_epsilon_r();

    // Apply absorption
    #pragma omp parallel for collapse(2)
    for (ssize_t i = 0; i < config.nx; ++i)
        for (ssize_t j = 0; j < config.ny; ++j) {
            double epsilon_factor = config.dt / epsilon_r(i, j);
            double absorption_factor = 1 - (sigma_x_r(i, j) + sigma_y_r(i, j)) * epsilon_factor / 2;
            absorption_factor = std::clamp(absorption_factor, 0.0, 1.0);  // Clipped to [0, 1] to ensure stability
            Ez_rw(i, j) *= absorption_factor;
        }
}

/**
 * @brief Update the field data at a specific time step.
 *
 * @param config Configuration containing simulation parameters.
 * @param Ez_time_r Reference to the 3D array holding the time evolution of Ez.
 * @param field_set FieldSet object containing the field data.
 */
void update_field(const Config &config, py_ref_rw<double, 3>& Ez_time_r, FieldSet& field_set)
{
    // Get reference to the electric field
    py_ref_r<double, 2> Ez_r = field_set.get_Ez_r();

    for (ssize_t i = 0; i < config.nx; ++i)
        for (ssize_t j = 0; j < config.ny; ++j)
            Ez_time_r(config.iteration, i, j) = Ez_r(i, j);
}


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
    py::array_t<double> Ez_time,
    const std::vector<double>& time_stamp,
    const py::array_t<double>& sigma_x,
    const py::array_t<double>& sigma_y,
    const py::array_t<double>& epsilon,
    const py::array_t<double>& gamma,
    const py::array_t<double>& n2,
    const double dt,
    const double mu_0,
    const size_t n_steps,
    const double dx,
    const double dy,
    const size_t nx,
    const size_t ny,
    std::vector<std::shared_ptr<BaseSource>>& sources
    )
{
    // Get mutable reference to the 3D array for Ez over time
    py_ref_rw<double, 3> Ez_time_r = Ez_time.mutable_unchecked<3>();

    // // Initialize MeshSet and FieldSet
    MeshSet mesh_set(epsilon, n2, gamma, mu_0, sigma_x, sigma_y);
    Config config(dx, dy, dt, nx, ny, time_stamp);
    FieldSet field_set(config);

    // Time-stepping loop
    for (size_t iteration = 0; iteration < n_steps; ++iteration)
    {
        // Update the magnetic fields Hx and Hy using Maxwell's equations
        update_magnetic_fields(config, mesh_set, field_set);

        // Update the electric field Ez using Maxwell's equations
        update_electric_field(config, field_set, mesh_set);

        // Apply Kerr effect to the electric field Ez
        // apply_kerr_effect(config, field_set, mesh_set);

        // Apply Third-Harmonic Generation (THG) to the electric field Ez
        apply_second_harmonic_generation(config, field_set, mesh_set);

        // Apply absorption to the electric field Ez
        apply_absorption(config, field_set, mesh_set);

        // Add source contributions to the electric field Ez
        for (auto& source : sources)
            source->add_to_field(config, field_set);

        // Update the field data for the current time step
        update_field(config, Ez_time_r, field_set);

        // Move to the next time step
        config.next();
    }
}


PYBIND11_MODULE(fdtd_simulation, module) {
    module.def("run_fdtd", &run_fdtd, "Run the FDTD simulation",
        py::arg("Ez"),
        py::arg("time_stamp"),
        py::arg("sigma_x"),
        py::arg("sigma_y"),
        py::arg("epsilon"),
        py::arg("gamma"),
        py::arg("n2"),
        py::arg("dt"),
        py::arg("mu_0"),
        py::arg("n_steps"),
        py::arg("dx"),
        py::arg("dy"),
        py::arg("nx"),
        py::arg("ny"),
        py::arg("sources")
    );
}