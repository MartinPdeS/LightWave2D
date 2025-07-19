#include "field_set.h"

FieldSet::FieldSet(const Config& config) : config(config)
{
    Hx = pybind11::array_t<double>({config.nx, config.ny});
    Hy = pybind11::array_t<double>({config.nx, config.ny});
    Ez = pybind11::array_t<double>({config.nx, config.ny});
    this->set_to_zero();
}


void FieldSet::set_to_zero() {
    py_ref_rw<double, 2>
        Ez_r = Ez.mutable_unchecked<2>(),
        Hx_r = Hx.mutable_unchecked<2>(),
        Hy_r = Hy.mutable_unchecked<2>();

    for (ssize_t i = 0; i < config.nx; ++i) {
        for (ssize_t j = 0; j < config.ny; ++j) {
            Ez_r(i, j) = 0.0;
            Hx_r(i, j) = 0.0;
            Hy_r(i, j) = 0.0;
        }
    }
}
