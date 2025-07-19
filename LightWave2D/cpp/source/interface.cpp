#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "source.h"

PYBIND11_MODULE(interface_source, module) {
    pybind11::class_<BaseSource, std::shared_ptr<BaseSource>>(module, "BaseSource");

    pybind11::class_<MultiWavelength, BaseSource, std::shared_ptr<MultiWavelength>>(module, "MultiWavelength")
        .def(
            pybind11::init<const pybind11::array_t<double>&, const pybind11::array_t<double>&, const pybind11::array_t<double>&, const pybind11::array_t<ssize_t>&>(),
            pybind11::arg("omega"),
            pybind11::arg("amplitude"),
            pybind11::arg("delay"),
            pybind11::arg("indexes")
        )
        .def("add_to_field", &MultiWavelength::add_to_field);

    pybind11::class_<Impulsion, BaseSource, std::shared_ptr<Impulsion>>(module, "Impulsion")
        .def(
            pybind11::init<const double, const double, const double, const pybind11::array_t<ssize_t>&>(),
            pybind11::arg("amplitude"),
            pybind11::arg("duration"),
            pybind11::arg("delay"),
            pybind11::arg("indexes")
        )
        .def("add_to_field", &Impulsion::add_to_field);
}
