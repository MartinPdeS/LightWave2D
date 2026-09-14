#include "simulator.h"


// Spatial differences are evaluated directly: no temporary gradient arrays.
void
FDTDSimulator::update_magnetic_fields(FieldSet& field_set) {
    auto Ez = field_set.get_Ez_r();
    auto Hx = field_set.get_Hx_rw();
    auto Hy = field_set.get_Hy_rw();
    #pragma omp parallel for collapse(2)
    for (int64_t i = 0; i < config.nx; ++i)
        for (int64_t j = 0; j < config.ny - 1; ++j)
            Hx(i, j) -= magnetic_y[i * config.ny + j] * ((Ez(i, j + 1) - Ez(i, j)) / config.dy);
    #pragma omp parallel for collapse(2)
    for (int64_t i = 0; i < config.nx - 1; ++i)
        for (int64_t j = 0; j < config.ny; ++j)
            Hy(i, j) += magnetic_x[i * config.ny + j] * ((Ez(i + 1, j) - Ez(i, j)) / config.dx);
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
    for (int64_t i = 1; i < config.nx - 1; ++i) {
        for (int64_t j = 1; j < config.ny - 1; ++j) {
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
    for (int64_t i = 0; i < config.nx; ++i) {
        for (int64_t j = 0; j < config.ny; ++j) {
            double intensity = Ez_rw(i, j) * Ez_rw(i, j);
            Ez_rw(i, j) += gamma_r(i, j) * intensity * config.dt;
        }
    }
}

void
FDTDSimulator::update_electric_field(FieldSet& field_set) {
    auto Ez = field_set.get_Ez_rw();
    auto Hx = field_set.get_Hx_rw();
    auto Hy = field_set.get_Hy_rw();
    #pragma omp parallel for collapse(2)
    for (int64_t i = 1; i < config.nx - 1; ++i)
        for (int64_t j = 1; j < config.ny - 1; ++j) {
            const double curl = (Hy(i, j) - Hy(i - 1, j)) / config.dx
                              - (Hx(i, j) - Hx(i, j - 1)) / config.dy;
            Ez(i, j) += electric[i * config.ny + j] * curl;
        }
}

void
FDTDSimulator::apply_absorption(FieldSet& field_set) {
    auto Ez = field_set.get_Ez_rw();
    #pragma omp parallel for collapse(2)
    for (int64_t i = 0; i < config.nx; ++i)
        for (int64_t j = 0; j < config.ny; ++j)
            Ez(i, j) *= absorption[i * config.ny + j];
}

void
FDTDSimulator::prepare_coefficients() {
    const size_t size = config.nx * config.ny;
    electric.resize(size);
    magnetic_x.resize(size);
    magnetic_y.resize(size);
    absorption.resize(size);
    const auto epsilon = mesh_set.get_epsilon_r();
    const auto sigma_x = mesh_set.get_sigma_x_r();
    const auto sigma_y = mesh_set.get_sigma_y_r();
    const double magnetic = config.dt / mesh_set.mu;
    for (int64_t i = 0; i < config.nx; ++i)
        for (int64_t j = 0; j < config.ny; ++j) {
            const size_t index = i * config.ny + j;
            electric[index] = config.dt / epsilon(i, j);
            magnetic_x[index] = magnetic * (1 - sigma_x(i, j) * magnetic / 2);
            magnetic_y[index] = magnetic * (1 - sigma_y(i, j) * magnetic / 2);
            absorption[index] = std::clamp(1 - (sigma_x(i, j) + sigma_y(i, j)) * electric[index] / 2, 0.0, 1.0);
        }
}

void
FDTDSimulator::update_field(py_ref_rw<double, 3>& Ez_time_r, FieldSet& field_set, const int64_t record_every)
{
    if (config.iteration % record_every != 0)
        return;

    const int64_t frame = config.iteration / record_every;
    if (frame >= Ez_time_r.shape(0))
        return;

    // Get reference to the electric field
    py_ref_r<double, 2> Ez_r = field_set.get_Ez_r();

    for (int64_t i = 0; i < config.nx; ++i)
        for (int64_t j = 0; j < config.ny; ++j)
            Ez_time_r(frame, i, j) = Ez_r(i, j);
}

void
FDTDSimulator::update_detectors(py_ref_rw<double, 2>& detector_data_r, py_ref_r<int64_t, 2>& detector_indexes_r, FieldSet& field_set, const int64_t record_every)
{
    if (config.iteration % record_every != 0)
        return;

    const int64_t frame = config.iteration / record_every;
    if (frame >= detector_data_r.shape(0))
        return;

    py_ref_r<double, 2> Ez_r = field_set.get_Ez_r();
    for (int64_t detector = 0; detector < detector_indexes_r.shape(0); ++detector)
        detector_data_r(frame, detector) = Ez_r(detector_indexes_r(detector, 0), detector_indexes_r(detector, 1));
}


void
FDTDSimulator::run(pybind11::array_t<double> Ez_time, const int64_t record_every, pybind11::array_t<double> detector_data, pybind11::array_t<int64_t> detector_indexes, int64_t detector_every)
{
    if (record_every < 1 || detector_every < 0)
        throw pybind11::value_error("Recording intervals must be positive.");
    if (detector_every == 0) detector_every = record_every;
    if (monitor_data.ndim() != 3 || monitor_data.shape(2) != 2 ||
        monitor_indexes.ndim() != 2 || monitor_indexes.shape(1) != 3 ||
        monitor_data.shape(1) != monitor_indexes.shape(0))
        throw pybind11::value_error("Invalid monitor buffer shapes.");
    auto monitors = monitor_data.mutable_unchecked<3>();
    auto locations = monitor_indexes.unchecked<2>();
    const int64_t points = locations.shape(0);
    if (points && monitors.shape(0) != (static_cast<int64_t>(config.time_stamp.size()) + detector_every - 1) / detector_every)
        throw pybind11::value_error("Invalid monitor sample count.");
    for (int64_t p = 0; p < points; ++p)
        if (locations(p, 0) < 1 || locations(p, 0) >= config.nx - 1 ||
            locations(p, 1) < 1 || locations(p, 1) >= config.ny - 1 ||
            locations(p, 2) < 0 || locations(p, 2) > 1)
            throw pybind11::value_error("Invalid monitor index or axis.");
    std::vector<double> previous_e(points);

    // Get mutable reference to the 3D array for Ez over time
    py_ref_rw<double, 3> Ez_time_r = Ez_time.mutable_unchecked<3>();
    py_ref_rw<double, 2> detector_data_r = detector_data.mutable_unchecked<2>();
    py_ref_r<int64_t, 2> detector_indexes_r = detector_indexes.unchecked<2>();

    // // Initialize MeshSet and FieldSet
    FieldSet field_set(this->config);
    prepare_coefficients();


    // Time-stepping loop
    for (size_t iteration = 0; iteration < this->config.time_stamp.size(); ++iteration)
    {
        const bool sample_monitors = iteration % detector_every == 0;
        if (sample_monitors) {
            auto Ez = field_set.get_Ez_r();
            for (int64_t p = 0; p < points; ++p)
                previous_e[p] = Ez(locations(p, 0), locations(p, 1));
        }
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
        this->update_field(Ez_time_r, field_set, record_every);
        this->update_detectors(detector_data_r, detector_indexes_r, field_set, detector_every);
        if (sample_monitors) {
            auto Ez = field_set.get_Ez_r();
            auto Hx = field_set.get_Hx_rw();
            auto Hy = field_set.get_Hy_rw();
            const int64_t frame = iteration / detector_every;
            for (int64_t p = 0; p < points; ++p) {
                const int64_t i = locations(p, 0), j = locations(p, 1);
                // Center E in time on H's half-step and H in space on Ez.
                monitors(frame, p, 0) = .5 * (previous_e[p] + Ez(i, j));
                monitors(frame, p, 1) = locations(p, 2) == 0
                    ? -.5 * (Hy(i - 1, j) + Hy(i, j))
                    : .5 * (Hx(i, j - 1) + Hx(i, j));
            }
        }

        // Do not advance beyond the final stored timestamp.
        if (iteration + 1 < this->config.time_stamp.size())
            config.next();
    }
}
