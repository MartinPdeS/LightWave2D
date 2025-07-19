#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "source.h"

namespace py = pybind11;

PYBIND11_MODULE(interface_source, m) {
    m.doc() = "Python bindings for FDTD simulation sources";

    // Abstract base class
    py::class_<BaseSource, std::shared_ptr<BaseSource>>(m, "BaseSource");

    // Multi-wavelength source
    py::class_<MultiWavelength, BaseSource, std::shared_ptr<MultiWavelength>>(m, "MultiWavelength")
        .def(
            py::init<const py::array_t<double>&, const py::array_t<double>&, const py::array_t<double>&, const py::array_t<ssize_t>&>(),
            py::arg("omega"),
            py::arg("amplitude"),
            py::arg("delay"),
            py::arg("indexes")
        )
        .def("add_to_field", &MultiWavelength::add_to_field, "Injects the source into the field");

    // Impulse source
    py::class_<Impulsion, BaseSource, std::shared_ptr<Impulsion>>(m, "Impulsion")
        .def(
            py::init<const double, const double, const double, const py::array_t<ssize_t>&>(),
            py::arg("amplitude"),
            py::arg("duration"),
            py::arg("delay"),
            py::arg("indexes")
        )
        .def("add_to_field", &Impulsion::add_to_field, "Injects the impulse into the field");
}
