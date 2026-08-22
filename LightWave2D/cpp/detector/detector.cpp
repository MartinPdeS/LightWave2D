#include "detector.h"

#include <pybind11/numpy.h>

namespace py = pybind11;

namespace {
double meter(const py::object& value) { return value.attr("to")("meter").attr("magnitude").cast<double>(); }
}

PointDetector::PointDetector(py::object grid_, py::tuple position, bool coherent_, py::object facecolor_, py::object edgecolor_, double alpha_, double rotation_)
    : grid(std::move(grid_)), facecolor(std::move(facecolor_)), edgecolor(std::move(edgecolor_)), coherent(coherent_), alpha(alpha_), rotation(rotation_) {
    if (position.size() != 2) throw py::value_error("position must contain exactly two coordinates.");
    p0 = grid.attr("get_coordinate")(py::arg("x") = position[0], py::arg("y") = position[1]);
    data = py::module_::import("numpy").attr("zeros")(grid.attr("n_steps"));
    time_stamp = grid.attr("time_stamp");
}

void PointDetector::update_data(py::object field, py::object new_time_stamp) {
    py::object numpy = py::module_::import("numpy");
    const int ndim = field.attr("ndim").cast<int>();
    if (ndim == 1)
        data = coherent ? field : numpy.attr("abs")(field);
    else {
        data = field.attr("__getitem__")(py::make_tuple(py::ellipsis(), p0.attr("x_index"), p0.attr("y_index")));
        if (!coherent) data = numpy.attr("abs")(data);
    }
    if (!new_time_stamp.is_none()) time_stamp = std::move(new_time_stamp);
}

void PointDetector::add_to_ax(const py::object& axis) const {
    axis.attr("scatter")(meter(p0.attr("x")), meter(p0.attr("y")), py::arg("color") = facecolor, py::arg("label") = "detector");
}

void PointDetector::plot() const {
    py::object pyplot = py::module_::import("matplotlib.pyplot");
    py::tuple items = pyplot.attr("subplots")(1, 1, py::arg("figsize") = py::make_tuple(6, 6)).cast<py::tuple>();
    py::object axis = items[1]; axis.attr("set_aspect")("equal"); add_to_ax(axis); pyplot.attr("show")();
}

void PointDetector::plot_data() const {
    py::object pyplot = py::module_::import("matplotlib.pyplot");
    py::tuple items = pyplot.attr("subplots")(1, 1, py::arg("figsize") = py::make_tuple(8, 4)).cast<py::tuple>();
    py::object axis = items[1]; axis.attr("plot")(time_stamp, data); axis.attr("set")(py::arg("ylabel") = "Amplitude", py::arg("xlabel") = "Time [seconds]"); pyplot.attr("show")();
}
