#include "pml.h"

#include <cmath>
#include <string>

#include <pybind11/numpy.h>

namespace py = pybind11;

namespace {
double meter(const py::object& value) { return value.attr("to")("meter").attr("magnitude").cast<double>(); }
double conductivity(const py::object& value) { return value.attr("to")("siemens/meter").attr("magnitude").cast<double>(); }
std::string percentage(py::object value) { std::string text = py::str(value).cast<std::string>(); return text.find('%') == std::string::npos ? text + "%" : text; }
}

PML::PML(py::object grid_, py::object width_, py::object sigma_max_, int order_)
    : grid(std::move(grid_)), width(std::move(width_)), sigma_max(std::move(sigma_max_)), order(order_) {
    if (order < 1) throw py::value_error("order must be at least 1.");
    const double width_percent = std::stod(percentage(width).substr(0, percentage(width).size() - 1));
    if (width_percent <= 0.0 || width_percent >= 50.0) throw py::value_error("width must be greater than 0% and less than 50%.");
    const std::string start = percentage(width);
    const std::string stop = std::to_string(100.0 - width_percent) + "%";
    width_start = grid.attr("get_coordinate")(py::arg("x") = start, py::arg("y") = start);
    width_stop = grid.attr("get_coordinate")(py::arg("x") = stop, py::arg("y") = stop);
    const int64_t nx = grid.attr("n_x").cast<int64_t>(), ny = grid.attr("n_y").cast<int64_t>();
    py::array_t<double> x({nx, ny}), y({nx, ny}); auto xv = x.mutable_unchecked<2>(); auto yv = y.mutable_unchecked<2>();
    const py::array_t<double> x_stamp = grid.attr("x_stamp").attr("to")("meter").attr("magnitude").cast<py::array_t<double>>();
    const py::array_t<double> y_stamp = grid.attr("y_stamp").attr("to")("meter").attr("magnitude").cast<py::array_t<double>>();
    const auto xs = x_stamp.unchecked<1>();
    const auto ys = y_stamp.unchecked<1>();
    const double start_x = meter(width_start.attr("x")), start_y = meter(width_start.attr("y"));
    const double stop_x = meter(width_stop.attr("x")), stop_y = meter(width_stop.attr("y"));
    const double maximum = conductivity(sigma_max);
    for (int64_t i = 0; i < nx; ++i) for (int64_t j = 0; j < ny; ++j) {
        const double left = xs(i) < start_x ? std::pow((start_x - xs(i)) / start_x, order) : 0.0;
        const double right = xs(i) > stop_x ? std::pow((xs(i) - stop_x) / start_x, order) : 0.0;
        const double bottom = ys(j) < start_y ? std::pow((start_y - ys(j)) / start_y, order) : 0.0;
        const double top = ys(j) > stop_y ? std::pow((ys(j) - stop_y) / start_y, order) : 0.0;
        xv(i, j) = maximum * (left + right); yv(i, j) = maximum * (bottom + top);
    }
    py::object unit = py::module_::import("TypedUnit").attr("ureg").attr("siemens") / py::module_::import("TypedUnit").attr("ureg").attr("meter");
    sigma_x = x * unit; sigma_y = y * unit;
}

void PML::add_to_ax(const py::object& axis) const {
    py::object colors = py::module_::import("matplotlib.colors"); py::object numpy = py::module_::import("numpy");
    py::object rgba = numpy.attr("zeros")(py::make_tuple(256, 4)); rgba.attr("__setitem__")(py::make_tuple(py::ellipsis(), 3), numpy.attr("linspace")(0, 1, 256));
    py::object cmap = colors.attr("ListedColormap")(rgba);
    py::object x = grid.attr("x_stamp").attr("to")("meter").attr("magnitude");
    py::object y = grid.attr("y_stamp").attr("to")("meter").attr("magnitude");
    py::object conductivity = sigma_y.attr("to")("siemens/meter").attr("magnitude") + sigma_x.attr("to")("siemens/meter").attr("magnitude");
    py::object transposed_conductivity = conductivity.attr("T");
    axis.attr("pcolormesh")(x, y, transposed_conductivity, py::arg("cmap") = cmap);
}

void PML::plot(int unit_size) const { py::object pyplot=py::module_::import("matplotlib.pyplot");py::tuple items=pyplot.attr("subplots")(1,1,py::arg("figsize")=py::make_tuple(unit_size,unit_size));py::object axis=items[1];axis.attr("set_aspect")("equal");add_to_ax(axis);pyplot.attr("show")(); }
