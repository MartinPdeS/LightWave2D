#include <pybind11/pybind11.h>

#include "grid.h"

namespace py = pybind11;

PYBIND11_MODULE(grid, module) {
    module.doc() = R"doc(
Unit-aware Cartesian simulation grid.

The grid stores cell-aligned coordinates and a Courant-stable time axis for
two-dimensional FDTD simulations.
)doc";
    py::class_<Grid>(module, "Grid", R"doc(
Cell-aligned two-dimensional FDTD grid.

Parameters
----------
resolution : pint.Quantity
    Positive spatial cell size.
size_x, size_y : pint.Quantity
    Positive physical extents of the grid.
n_steps : int, default=200
    Number of temporal samples.
)doc")
        .def(py::init<py::object, py::object, py::object, int64_t>(), py::arg("resolution"), py::arg("size_x"), py::arg("size_y"), py::arg("n_steps") = 200)
        .def("get_distance_grid", &Grid::get_distance_grid, py::arg("x0") = 0.0, py::arg("y0") = 0.0, R"doc(
Return distances from a physical point.

Parameters
----------
x0, y0 : float or pint.Quantity
    Reference coordinates.

Returns
-------
numpy.ndarray
    Unit-bearing distance mesh.
)doc")
        .def("get_coordinate", &Grid::get_coordinate, py::arg("x") = py::none(), py::arg("y") = py::none(), R"doc(
Resolve named or physical coordinates to cell-aligned values and indexes.

Parameters
----------
x, y : str or pint.Quantity, optional
    Physical coordinates, named boundaries, ``"center"``, or percentages.

Returns
-------
types.SimpleNamespace
    Contains supplied coordinates and corresponding integer indexes.
)doc")
        .def("parse_x_position", &Grid::parse_x_position)
        .def("parse_y_position", &Grid::parse_y_position)
        .def_readonly("resolution", &Grid::resolution).def_readonly("size_x", &Grid::size_x).def_readonly("size_y", &Grid::size_y)
        .def_readonly("n_x", &Grid::n_x).def_readonly("n_y", &Grid::n_y).def_readonly("n_steps", &Grid::n_steps)
        .def_readonly("dx", &Grid::dx).def_readonly("dy", &Grid::dy).def_readonly("dt", &Grid::dt)
        .def_readonly("shape", &Grid::shape).def_readonly("time_stamp", &Grid::time_stamp)
        .def_readonly("x_stamp", &Grid::x_stamp).def_readonly("y_stamp", &Grid::y_stamp)
        .def_readonly("x_mesh", &Grid::x_mesh).def_readonly("y_mesh", &Grid::y_mesh).def_readonly("polygon", &Grid::polygon);
}
