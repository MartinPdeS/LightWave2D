#include "grid.h"

#include <algorithm>
#include <cmath>
#include <stdexcept>

namespace py = pybind11;

Grid::Grid(py::object resolution_, py::object size_x_, py::object size_y_, int64_t n_steps_)
    : resolution(std::move(resolution_)), size_x(std::move(size_x_)), size_y(std::move(size_y_)), n_steps(n_steps_) {
    ureg_ = py::module_::import("TypedUnit").attr("ureg");
    const double resolution_m = meter_value(resolution);
    const double size_x_m = meter_value(size_x);
    const double size_y_m = meter_value(size_y);
    if (resolution_m <= 0.0 || size_x_m <= 0.0 || size_y_m <= 0.0)
        throw py::value_error("resolution and grid sizes must be positive.");
    if (n_steps < 1)
        throw py::value_error("n_steps must be at least 1.");
    n_x = static_cast<int64_t>(size_x_m / resolution_m);
    n_y = static_cast<int64_t>(size_y_m / resolution_m);
    if (n_x < 2 || n_y < 2)
        throw py::value_error("Grid dimensions must each contain at least two cells.");

    dx = size_x / py::int_(n_x);
    dy = size_y / py::int_(n_y);
    const double dx_m = meter_value(dx);
    const double dy_m = meter_value(dy);
    dt = meter_quantity(1.0 / (299792458.0 * std::sqrt(1.0 / (dx_m * dx_m) + 1.0 / (dy_m * dy_m)))).attr("to")("meter") / ureg_.attr("meter") * ureg_.attr("second");
    shape = py::make_tuple(n_x, n_y);

    py::object numpy = py::module_::import("numpy");
    time_stamp = numpy.attr("arange")(n_steps) * dt.attr("to")("second");
    x_stamp = numpy.attr("arange")(n_x) * dx;
    y_stamp = numpy.attr("arange")(n_y) * dy;
    py::tuple meshes = numpy.attr("meshgrid")(x_stamp, y_stamp).cast<py::tuple>();
    x_mesh = meshes[0];
    y_mesh = meshes[1];
    py::object polygon_type = py::module_::import("shapely.geometry").attr("Polygon");
    py::object points = py::make_tuple(
        py::make_tuple(0.0, 0.0), py::make_tuple(0.0, meter_value(y_stamp.attr("__getitem__")(-1))),
        py::make_tuple(meter_value(x_stamp.attr("__getitem__")(-1)), 0.0),
        py::make_tuple(meter_value(x_stamp.attr("__getitem__")(-1)), meter_value(y_stamp.attr("__getitem__")(-1))));
    polygon = polygon_type(points).attr("convex_hull");
}

double Grid::meter_value(const py::object& value) const {
    py::object quantity = value;
    if (py::hasattr(quantity, "to")) quantity = quantity.attr("to")("meter").attr("magnitude");
    return quantity.cast<double>();
}

py::object Grid::meter_quantity(double value) const { return py::float_(value) * ureg_.attr("meter"); }

py::object Grid::parse_position(py::object value, bool is_x) const {
    if (!py::isinstance<py::str>(value)) return value;
    const std::string text = py::str(value).cast<std::string>();
    const py::object stamp = is_x ? x_stamp : y_stamp;
    if (text.find('%') != std::string::npos) {
        const double percentage = std::stod(text.substr(0, text.size() - 1)) / 100.0;
        return stamp.attr("__getitem__")(0) + py::float_(percentage) * (stamp.attr("__getitem__")(-1) - stamp.attr("__getitem__")(0));
    }
    if (is_x) {
        if (text == "left") return stamp.attr("__getitem__")(0);
        if (text == "center") return py::module_::import("numpy").attr("mean")(stamp);
        if (text == "right") return stamp.attr("__getitem__")(-1);
        throw py::value_error("Invalid x position. Use left, center, right, or a percentage.");
    }
    if (text == "bottom") return stamp.attr("__getitem__")(0);
    if (text == "center") return py::module_::import("numpy").attr("mean")(stamp);
    if (text == "top") return stamp.attr("__getitem__")(-1);
    throw py::value_error("Invalid y position. Use bottom, center, top, or a percentage.");
}

py::object Grid::parse_x_position(py::object value) const { return parse_position(std::move(value), true); }
py::object Grid::parse_y_position(py::object value) const { return parse_position(std::move(value), false); }

py::object Grid::get_coordinate(py::object x, py::object y) const {
    py::object namespace_ = py::module_::import("types").attr("SimpleNamespace")();
    if (!x.is_none()) {
        py::object x_value = py::module_::import("numpy").attr("clip")(parse_x_position(x), x_stamp.attr("__getitem__")(0), x_stamp.attr("__getitem__")(-1));
        const double x_m = meter_value(x_value);
        namespace_.attr("x") = x_value;
        namespace_.attr("x_index") = std::min(static_cast<int64_t>(x_m / meter_value(dx)), n_x - 1);
    }
    if (!y.is_none()) {
        py::object y_value = py::module_::import("numpy").attr("clip")(parse_y_position(y), y_stamp.attr("__getitem__")(0), y_stamp.attr("__getitem__")(-1));
        const double y_m = meter_value(y_value);
        namespace_.attr("y") = y_value;
        namespace_.attr("y_index") = std::min(static_cast<int64_t>(y_m / meter_value(dy)), n_y - 1);
    }
    return namespace_;
}

py::object Grid::get_distance_grid(py::object x0, py::object y0) const {
    py::tuple meshes = py::module_::import("numpy").attr("meshgrid")(x_stamp, y_stamp).cast<py::tuple>();
    py::object x_mesh_ = meshes[0];
    py::object y_mesh_ = meshes[1];
    return py::module_::import("numpy").attr("sqrt")((x_mesh_ - x0) * (x_mesh_ - x0) + (y_mesh_ - y0) * (y_mesh_ - y0));
}
