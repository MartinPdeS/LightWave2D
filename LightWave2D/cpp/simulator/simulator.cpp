#include "simulator.h"


// void
std::tuple<pybind11::array_t<double>, pybind11::array_t<double>>
FDTDSimulator::compute_yee_gradients(FieldSet& field_set)
{
    // Initialize gradient arrays
    pybind11::array_t<double> dEz_dx({config.nx - 1, config.ny});
    pybind11::array_t<double> dEz_dy({config.nx, config.ny - 1});

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


void
FDTDSimulator::update_magnetic_fields(FieldSet& field_set) {
    // Compute Yee gradients of the electric field
    auto [dEz_dx, dEz_dy] = compute_yee_gradients(field_set);

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

// void
std::tuple<pybind11::array_t<double>, pybind11::array_t<double>>
FDTDSimulator::compute_magnetic_field_gradients(FieldSet& field_set)
{
    // Initialize gradient arrays
    pybind11::array_t<double> dHy_dx({config.nx - 1, config.ny - 1});
    pybind11::array_t<double> dHx_dy({config.nx - 1, config.ny - 1});

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


void
FDTDSimulator::apply_kerr_effect(FieldSet& field_set)
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


void
FDTDSimulator::apply_second_harmonic_generation(FieldSet& field_set)
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

void
FDTDSimulator::update_electric_field(FieldSet& field_set)
{
    // Compute the Yee gradients of the magnetic fields Hx and Hy
    auto [dHy_dx, dHx_dy] = compute_magnetic_field_gradients(field_set);

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

void
FDTDSimulator::apply_absorption(FieldSet &field_set) {
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


void
FDTDSimulator::update_field(py_ref_rw<double, 3>& Ez_time_r, FieldSet& field_set)
{
    // Get reference to the electric field
    py_ref_r<double, 2> Ez_r = field_set.get_Ez_r();

    for (ssize_t i = 0; i < config.nx; ++i)
        for (ssize_t j = 0; j < config.ny; ++j)
            Ez_time_r(config.iteration, i, j) = Ez_r(i, j);
}


void
FDTDSimulator::run(pybind11::array_t<double> Ez_time)
{
    // Get mutable reference to the 3D array for Ez over time
    py_ref_rw<double, 3> Ez_time_r = Ez_time.mutable_unchecked<3>();

    // // Initialize MeshSet and FieldSet
    FieldSet field_set(this->config);


    // Time-stepping loop
    for (size_t iteration = 0; iteration < this->config.time_stamp.size(); ++iteration)
    {
        // Update the magnetic fields Hx and Hy using Maxwell's equations
        this->update_magnetic_fields(field_set);

        // Update the electric field Ez using Maxwell's equations
        this->update_electric_field(field_set);

        // Apply Kerr effect to the electric field Ez
        // apply_kerr_effect(config, field_set, mesh_set);

        // Apply Third-Harmonic Generation (THG) to the electric field Ez
        this->apply_second_harmonic_generation(field_set);

        // Apply absorption to the electric field Ez
        this->apply_absorption(field_set);

        // Add source contributions to the electric field Ez
        for (auto& source : sources)
            source->add_to_field(config, field_set);

        // Update the field data for the current time step
        this->update_field(Ez_time_r, field_set);

        // Move to the next time step
        config.next();
    }
}
