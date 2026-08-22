#include "./source.h"

#include <cstdlib>
#include <stdexcept>

PointGeometry::PointGeometry(int64_t x_index, int64_t y_index)
{
    if (x_index < 0 || y_index < 0)
        throw std::invalid_argument("Point-source indexes must be non-negative.");
    indexes_.push_back({x_index, y_index});
}

LineGeometry::LineGeometry(int64_t x0, int64_t y0, int64_t x1, int64_t y1)
{
    if (x0 < 0 || y0 < 0 || x1 < 0 || y1 < 0)
        throw std::invalid_argument("Line-source indexes must be non-negative.");

    const int64_t dx = std::abs(x1 - x0);
    const int64_t dy = std::abs(y1 - y0);
    const int64_t step_x = x0 <= x1 ? 1 : -1;
    const int64_t step_y = y0 <= y1 ? 1 : -1;
    int64_t error = dx - dy;

    while (true) {
        indexes_.push_back({x0, y0});
        if (x0 == x1 && y0 == y1)
            break;

        const int64_t doubled_error = 2 * error;
        if (doubled_error > -dy) {
            error -= dy;
            x0 += step_x;
        }
        if (doubled_error < dx) {
            error += dx;
            y0 += step_y;
        }
    }
}

MultiWavelength::MultiWavelength(const pybind11::array_t<double>& omega_list, const pybind11::array_t<double>& amplitude_list, const pybind11::array_t<double>& delay_list, const pybind11::array_t<int64_t>& indexes)
: omega_list(omega_list), amplitude_list(amplitude_list), delay_list(delay_list), indexes(indexes)
{
    if (omega_list.ndim() != 1 || amplitude_list.ndim() != 1 || delay_list.ndim() != 1)
        throw std::invalid_argument("Wave-source frequency, amplitude, and delay arrays must be one-dimensional.");
    if (omega_list.shape(0) != amplitude_list.shape(0) || omega_list.shape(0) != delay_list.shape(0))
        throw std::invalid_argument("Wave-source frequency, amplitude, and delay arrays must have the same length.");
    if (indexes.ndim() != 2 || indexes.shape(1) != 2)
        throw std::invalid_argument("Source indexes must have shape (n, 2).");
}

void MultiWavelength::add_to_field(const Config& config, FieldSet &field_set) {
    py_ref_rw<double, 2> Ez_rw = field_set.get_Ez_rw();
    py_ref_r<int64_t, 2> idx_r = indexes.unchecked<2>();
    py_ref_r<double, 1> omega_list_r = omega_list.unchecked<1>();
    py_ref_r<double, 1> amplitude_list_r = amplitude_list.unchecked<1>();
    py_ref_r<double, 1> delay_list_r = delay_list.unchecked<1>();

    for (int64_t i = 0; i < idx_r.shape(0); ++i) {
        size_t x = static_cast<size_t>(idx_r(i, 0));
        size_t y = static_cast<size_t>(idx_r(i, 1));

        for (int64_t j = 0; j < omega_list_r.shape(0); ++j){
            double omega = omega_list_r(j);
            double amplitude = amplitude_list_r(j);
            double delay = delay_list_r(j);

            Ez_rw(x, y) += amplitude * std::cos(omega * config.time + delay);
        }
    }
}

Pulse::Pulse(const double amplitude, const double duration, const double delay, const pybind11::array_t<int64_t>& indexes)
: amplitude(amplitude), duration(duration), delay(delay), indexes(indexes)
{
    if (duration <= 0.0)
        throw std::invalid_argument("Pulse duration must be positive.");
    if (indexes.ndim() != 2 || indexes.shape(1) != 2)
        throw std::invalid_argument("Source indexes must have shape (n, 2).");
}

void Pulse::add_to_field(const Config& config, FieldSet &field_set) {
    py_ref_rw<double, 2> Ez_rw = field_set.get_Ez_rw();
    py_ref_r<int64_t, 2> idx_r = indexes.unchecked<2>();

    for (int64_t i = 0; i < idx_r.shape(0); ++i) {
        size_t x = static_cast<size_t>(idx_r(i, 0));
        size_t y = static_cast<size_t>(idx_r(i, 1));

        double factor = ((config.time - delay) / duration);
        factor = std::exp(- (factor * factor));

        Ez_rw(x, y) += amplitude * factor;
    }
}
