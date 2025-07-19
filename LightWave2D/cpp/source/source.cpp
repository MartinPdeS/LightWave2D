#include "./source.h"

MultiWavelength::MultiWavelength(const pybind11::array_t<double>& omega_list, const pybind11::array_t<double>& amplitude_list, const pybind11::array_t<double>& delay_list, const pybind11::array_t<ssize_t>& indexes)
: omega_list(omega_list), amplitude_list(amplitude_list), delay_list(delay_list), indexes(indexes)
{

}

void MultiWavelength::add_to_field(const Config& config, FieldSet &field_set) {
    py_ref_rw<double, 2> Ez_rw = field_set.get_Ez_rw();
    py_ref_r<ssize_t, 2> idx_r = indexes.unchecked<2>();
    py_ref_r<double, 1> omega_list_r = omega_list.unchecked<1>();
    py_ref_r<double, 1> amplitude_list_r = amplitude_list.unchecked<1>();
    py_ref_r<double, 1> delay_list_r = delay_list.unchecked<1>();

    for (ssize_t i = 0; i < idx_r.shape(0); ++i) {
        size_t x = static_cast<size_t>(idx_r(i, 0));
        size_t y = static_cast<size_t>(idx_r(i, 1));

        for (ssize_t j = 0; j < omega_list_r.shape(0); ++j){
            double omega = omega_list_r(j);
            double amplitude = amplitude_list_r(j);
            double delay = delay_list_r(j);

            Ez_rw(x, y) += amplitude * std::cos(omega * config.time + delay);
        }
    }
}

Impulsion::Impulsion(const double amplitude, const double duration, const double delay, const pybind11::array_t<ssize_t>& indexes)
: amplitude(amplitude), duration(duration), delay(delay), indexes(indexes)
{

}

void Impulsion::add_to_field(const Config& config, FieldSet &field_set) {
    py_ref_rw<double, 2> Ez_rw = field_set.get_Ez_rw();
    py_ref_r<ssize_t, 2> idx_r = indexes.unchecked<2>();

    for (ssize_t i = 0; i < idx_r.shape(0); ++i) {
        size_t x = static_cast<size_t>(idx_r(i, 0));
        size_t y = static_cast<size_t>(idx_r(i, 1));

        double factor = ((config.time - delay) / duration);
        factor = std::exp(- (factor * factor));

        Ez_rw(x, y) += amplitude * factor;
    }
}

