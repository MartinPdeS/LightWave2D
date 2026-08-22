#include <pybind11/pybind11.h>

#include "detector.h"

namespace py = pybind11;

PYBIND11_MODULE(detector, module) {
    module.doc() = "Native detector models for LightWave2D.";
    py::class_<PointDetector>(module, "PointDetector", R"doc(
Point detector that samples an FDTD field at one grid cell.

Parameters
----------
grid : LightWave2D.grid.Grid
    Simulation grid used to resolve ``position``.
position : tuple
    Physical or named ``(x, y)`` position.
coherent : bool, default=True
    Retain signed field samples; otherwise store magnitudes.
)doc")
        .def(py::init<py::object, py::tuple, bool, py::object, py::object, double, double>(), py::arg("grid"), py::arg("position"), py::arg("coherent") = true, py::arg("facecolor") = "green", py::arg("edgecolor") = "green", py::arg("alpha") = 0.8, py::arg("rotation") = 0.0)
        .def("update_data", &PointDetector::update_data, py::arg("field"), py::arg("time_stamp") = py::none(), R"doc(
Update the detector signal from a field history or already sampled vector.

Parameters
----------
field : numpy.ndarray
    One-dimensional detector samples or ``(time, nx, ny)`` field data.
time_stamp : numpy.ndarray, optional
    Time values corresponding to the supplied samples.
)doc")
        .def("add_to_ax", &PointDetector::add_to_ax).def("plot", &PointDetector::plot).def("plot_data", &PointDetector::plot_data)
        .def_readonly("grid", &PointDetector::grid).def_readonly("p0", &PointDetector::p0)
        .def_readwrite("data", &PointDetector::data).def_readwrite("time_stamp", &PointDetector::time_stamp)
        .def_readonly("coherent", &PointDetector::coherent).def_readonly("facecolor", &PointDetector::facecolor).def_readonly("edgecolor", &PointDetector::edgecolor)
        .def_readonly("alpha", &PointDetector::alpha).def_readonly("rotation", &PointDetector::rotation);
    module.attr("BaseDetector") = module.attr("PointDetector");
}
