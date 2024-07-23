#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include "config.cpp"
#include "field_set.cpp"

namespace py = pybind11;
#define py_ref_rw py::detail::unchecked_mutable_reference
#define py_ref_r py::detail::unchecked_reference

class BaseSource {
public:
    virtual ~BaseSource() {}
    virtual void add_to_field(const Config& config, FieldSet &field_set) = 0;
};

class MultiWavelength : public BaseSource {
public:
    py::array_t<double> omega_list;
    py::array_t<double> amplitude_list;
    py::array_t<double> delay_list;
    py::array_t<ssize_t> indexes;  // Nx2 elements (x, y)

    MultiWavelength(
        const py::array_t<double>& omega_list,
        const py::array_t<double>& amplitude_list,
        const py::array_t<double>& delay_list,
        const py::array_t<ssize_t>& indexes)
    : omega_list(omega_list), amplitude_list(amplitude_list), delay_list(delay_list), indexes(indexes) {}

    void add_to_field(const Config& config, FieldSet &field_set) override {
        py_ref_rw<double, 2> Ez_rw = field_set.get_Ez_rw();
        py_ref_r<ssize_t, 2> idx_r = indexes.unchecked<2>();
        py_ref_r<double, 1> omega_list_r = omega_list.unchecked<1>();
        py_ref_r<double, 1> amplitude_list_r = amplitude_list.unchecked<1>();
        py_ref_r<double, 1> delay_list_r = delay_list.unchecked<1>();

        for (ssize_t i = 0; i < idx_r.shape(0); ++i) {
            size_t x = static_cast<size_t>(idx_r(i, 0));
            size_t y = static_cast<size_t>(idx_r(i, 1));
            // Ez_rw(x, y) = 0;

            for (ssize_t j = 0; j < omega_list_r.shape(0); ++j){
                double omega = omega_list_r(j);
                double amplitude = amplitude_list_r(j);
                double delay = delay_list_r(j);

                Ez_rw(x, y) += amplitude * std::cos(omega * config.time + delay);
            }
        }
    }
};

class Impulsion : public BaseSource {
public:
    double amplitude;
    double duration;
    double delay;
    py::array_t<ssize_t> indexes;  // Nx2 elements (x, y)

    Impulsion(
        double amplitude,
        double duration,
        double delay,
        const py::array_t<ssize_t>& indexes)
    : amplitude(amplitude), duration(duration), delay(delay), indexes(indexes) {}

    void add_to_field(const Config& config, FieldSet &field_set) override {
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
};

PYBIND11_MODULE(SourceInterface, module) {
    py::class_<BaseSource, std::shared_ptr<BaseSource>>(module, "BaseSource");

    py::class_<MultiWavelength, BaseSource, std::shared_ptr<MultiWavelength>>(module, "MultiWavelength")
        .def(
            py::init<const py::array_t<double>&, const py::array_t<double>&, const py::array_t<double>&, const py::array_t<ssize_t>&>(),
            py::arg("omega"),
            py::arg("amplitude"),
            py::arg("delay"),
            py::arg("indexes")
        )
        .def("add_to_field", &MultiWavelength::add_to_field);

    py::class_<Impulsion, BaseSource, std::shared_ptr<Impulsion>>(module, "Impulsion")
        .def(
            py::init<const double, const double, const double, const py::array_t<ssize_t>&>(),
            py::arg("amplitude"),
            py::arg("duration"),
            py::arg("delay"),
            py::arg("indexes")
        )
        .def("add_to_field", &Impulsion::add_to_field);
}
