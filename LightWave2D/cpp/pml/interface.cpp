#include <pybind11/pybind11.h>

#include "pml.h"

namespace py = pybind11;

PYBIND11_MODULE(pml, module) {
    module.doc() = R"doc(
Native perfectly matched layer profiles for LightWave2D.

Conductivity rises polynomially at the grid boundaries to suppress outgoing
wave reflections.
)doc";
    py::object ureg = py::module_::import("TypedUnit").attr("ureg");
    py::class_<PML>(module, "PML", R"doc(
Perfectly matched layer conductivity profile.

Parameters
----------
grid : LightWave2D.grid.Grid
    Grid on which to build the boundary profiles.
width : str, default="10%"
    Width of each absorbing boundary region as a percentage below 50.
sigma_max : pint.Quantity, default=0.045 S/m
    Conductivity at the outer boundary.
order : int, default=3
    Positive polynomial grading order.
)doc")
        .def(py::init<py::object, py::object, py::object, int>(), py::arg("grid"), py::arg("width") = "10%", py::arg("sigma_max") = py::float_(0.045) * ureg.attr("siemens") / ureg.attr("meter"), py::arg("order") = 3)
        .def("add_to_ax", &PML::add_to_ax).def("plot", &PML::plot, py::arg("unit_size") = 6)
        .def_readonly("grid", &PML::grid).def_readonly("width", &PML::width).def_readonly("sigma_max", &PML::sigma_max).def_readonly("order", &PML::order)
        .def_readonly("sigma_x", &PML::sigma_x).def_readonly("sigma_y", &PML::sigma_y).def_readonly("width_start", &PML::width_start).def_readonly("width_stop", &PML::width_stop);
}
