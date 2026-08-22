#include <cmath>
#include <cstdint>
#include <memory>
#include <stdexcept>
#include <utility>

#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "source.h"

namespace py = pybind11;

namespace {

py::array_t<int64_t> indexes_to_numpy(const SourceGeometry& geometry) {
    const auto& indexes = geometry.indexes();
    py::array_t<int64_t> result({static_cast<py::ssize_t>(indexes.size()), static_cast<py::ssize_t>(2)});
    auto view = result.mutable_unchecked<2>();
    for (std::size_t i = 0; i < indexes.size(); ++i) {
        view(static_cast<py::ssize_t>(i), 0) = indexes[i][0];
        view(static_cast<py::ssize_t>(i), 1) = indexes[i][1];
    }
    return result;
}

py::array_t<double> quantity_array(py::object value, const char* unit = nullptr) {
    if (unit != nullptr && py::hasattr(value, "to"))
        value = value.attr("to")(unit).attr("magnitude");
    auto numpy = py::module_::import("numpy");
    return numpy.attr("atleast_1d")(numpy.attr("asarray")(value, py::arg("dtype") = "float64")).cast<py::array_t<double>>();
}

double quantity_scalar(py::object value, const char* unit) {
    const auto values = quantity_array(std::move(value), unit);
    if (values.size() != 1)
        throw py::value_error("Expected one scalar value.");
    return *values.data();
}

py::object grid_coordinate(const py::object& grid, const py::tuple& position) {
    if (position.size() != 2)
        throw py::value_error("position must contain exactly two values.");
    return grid.attr("get_coordinate")(py::arg("x") = position[0], py::arg("y") = position[1]);
}

py::array_t<int64_t> point_indexes(const py::object& coordinate) {
    return indexes_to_numpy(PointGeometry(coordinate.attr("x_index").cast<int64_t>(), coordinate.attr("y_index").cast<int64_t>()));
}

py::array_t<int64_t> line_indexes(const py::object& p0, const py::object& p1) {
    return indexes_to_numpy(LineGeometry(
        p0.attr("x_index").cast<int64_t>(), p0.attr("y_index").cast<int64_t>(),
        p1.attr("x_index").cast<int64_t>(), p1.attr("y_index").cast<int64_t>()));
}

struct WaveArguments {
    py::array_t<double> omega, amplitude, delay;
    py::array_t<int64_t> indexes;
};

WaveArguments make_wave_arguments(py::object wavelength, py::object amplitude, py::array_t<int64_t> indexes) {
    auto wavelengths = quantity_array(std::move(wavelength), "meter");
    auto amplitudes = quantity_array(std::move(amplitude));
    if (wavelengths.ndim() != 1 || amplitudes.ndim() != 1 || wavelengths.size() == 0 || wavelengths.size() != amplitudes.size())
        throw py::value_error("wavelength and amplitude must be non-empty one-dimensional arrays of equal length.");
    py::array_t<double> omega(wavelengths.size()), delay(wavelengths.size());
    auto w = wavelengths.unchecked<1>(); auto o = omega.mutable_unchecked<1>(); auto d = delay.mutable_unchecked<1>();
    for (py::ssize_t i = 0; i < wavelengths.size(); ++i) {
        if (w(i) <= 0.0) throw py::value_error("wavelength values must be positive.");
        o(i) = 2.0 * std::acos(-1.0) * 299792458.0 / w(i); d(i) = 0.0;
    }
    return {std::move(omega), std::move(amplitudes), std::move(delay), std::move(indexes)};
}

class Appearance {
public:
    Appearance(py::object facecolor, double alpha) : facecolor_(std::move(facecolor)), alpha_(alpha) {}
    virtual ~Appearance() = default;
    virtual void add_to_ax(const py::object& ax) const = 0;
    void plot() const {
        auto pyplot = py::module_::import("matplotlib.pyplot");
        auto figure_axes = pyplot.attr("subplots")(1, 1, py::arg("figsize") = py::make_tuple(6, 6)).cast<py::tuple>();
        py::object ax = figure_axes[1]; ax.attr("set_aspect")("equal"); add_to_ax(ax); pyplot.attr("show")();
    }
protected: py::object facecolor_; double alpha_;
};

class PointWaveSource final : public MultiWavelength, public Appearance {
public:
    PointWaveSource(py::object grid, py::object wavelength, py::tuple position, py::object amplitude, py::object edgecolor = py::str("red"), py::object facecolor = py::str("red"), double alpha = .3)
        : PointWaveSource(make_wave_arguments(wavelength, amplitude, point_indexes(grid_coordinate(grid, position))), grid_coordinate(grid, position), std::move(facecolor), alpha) {}
    void add_to_ax(const py::object& ax) const override { ax.attr("scatter")(quantity_scalar(coordinate_.attr("x"), "meter"), quantity_scalar(coordinate_.attr("y"), "meter"), py::arg("color") = facecolor_, py::arg("label") = "source"); }
private:
    PointWaveSource(WaveArguments args, py::object coordinate, py::object facecolor, double alpha)
        : MultiWavelength(args.omega, args.amplitude, args.delay, args.indexes), Appearance(std::move(facecolor), alpha), coordinate_(std::move(coordinate)) {}
    py::object coordinate_;
};

class LineWaveSource final : public MultiWavelength, public Appearance {
public:
    LineWaveSource(py::object grid, py::object wavelength, py::tuple position_0, py::tuple position_1, py::object amplitude, py::object edgecolor = py::str("red"), py::object facecolor = py::str("red"), double alpha = .3)
        : LineWaveSource(make_wave_arguments(wavelength, amplitude, line_indexes(grid_coordinate(grid, position_0), grid_coordinate(grid, position_1))), grid_coordinate(grid, position_0), grid_coordinate(grid, position_1), std::move(facecolor), alpha) {}
    void add_to_ax(const py::object& ax) const override { ax.attr("plot")(py::make_tuple(quantity_scalar(p0_.attr("x"), "meter"), quantity_scalar(p1_.attr("x"), "meter")), py::make_tuple(quantity_scalar(p0_.attr("y"), "meter"), quantity_scalar(p1_.attr("y"), "meter")), py::arg("color") = facecolor_, py::arg("label") = "source"); }
private:
    LineWaveSource(WaveArguments args, py::object p0, py::object p1, py::object facecolor, double alpha)
        : MultiWavelength(args.omega, args.amplitude, args.delay, args.indexes), Appearance(std::move(facecolor), alpha), p0_(std::move(p0)), p1_(std::move(p1)) {}
    py::object p0_, p1_;
};

class PointPulseSource final : public Pulse, public Appearance {
public:
    PointPulseSource(py::object grid, double amplitude, py::object duration, py::tuple position, py::object delay = py::float_(0.), py::object edgecolor = py::str("red"), py::object facecolor = py::str("red"), double alpha = .3)
        : Pulse(amplitude, quantity_scalar(duration, "second"), quantity_scalar(delay, "second"), point_indexes(grid_coordinate(grid, position))), Appearance(std::move(facecolor), alpha), coordinate_(grid_coordinate(grid, position)) {}
    void add_to_ax(const py::object& ax) const override { ax.attr("scatter")(quantity_scalar(coordinate_.attr("x"), "meter"), quantity_scalar(coordinate_.attr("y"), "meter"), py::arg("color") = facecolor_, py::arg("label") = "source"); }
private: py::object coordinate_;
};

class LinePulseSource final : public Pulse, public Appearance {
public:
    LinePulseSource(py::object grid, double amplitude, py::object duration, py::tuple position_0, py::tuple position_1, py::object delay = py::float_(0.), py::object edgecolor = py::str("red"), py::object facecolor = py::str("red"), double alpha = .3)
        : Pulse(amplitude, quantity_scalar(duration, "second"), quantity_scalar(delay, "second"), line_indexes(grid_coordinate(grid, position_0), grid_coordinate(grid, position_1))), Appearance(std::move(facecolor), alpha), p0_(grid_coordinate(grid, position_0)), p1_(grid_coordinate(grid, position_1)) {}
    void add_to_ax(const py::object& ax) const override { ax.attr("plot")(py::make_tuple(quantity_scalar(p0_.attr("x"), "meter"), quantity_scalar(p1_.attr("x"), "meter")), py::make_tuple(quantity_scalar(p0_.attr("y"), "meter"), quantity_scalar(p1_.attr("y"), "meter")), py::arg("color") = facecolor_, py::arg("label") = "source"); }
private: py::object p0_, p1_;
};

}  // namespace

PYBIND11_MODULE(source, module) {
    module.doc() = R"doc(
Native excitation sources for LightWave2D.

Sources combine a waveform with point or line geometry and inject their values
into the native FDTD field update.
)doc";
    py::class_<BaseSource, std::shared_ptr<BaseSource>>(module, "BaseSource", R"doc(
Abstract FDTD source.

Notes
-----
Instantiate one of the point or line waveform subclasses instead.
)doc");
    py::class_<SourceGeometry>(module, "SourceGeometry", "Discrete grid geometry occupied by a source.").def_property_readonly("indexes", &indexes_to_numpy, "Grid indexes with shape (n_points, 2).");
    py::class_<PointGeometry, SourceGeometry>(module, "PointGeometry").def(py::init<int64_t, int64_t>(), py::arg("x_index"), py::arg("y_index"));
    py::class_<LineGeometry, SourceGeometry>(module, "LineGeometry").def(py::init<int64_t, int64_t, int64_t, int64_t>(), py::arg("x0"), py::arg("y0"), py::arg("x1"), py::arg("y1"));
    py::class_<MultiWavelength, BaseSource, std::shared_ptr<MultiWavelength>>(module, "MultiWavelength").def(py::init<const py::array_t<double>&, const py::array_t<double>&, const py::array_t<double>&, const py::array_t<int64_t>&>()).def("add_to_field", &MultiWavelength::add_to_field).def_property_readonly("_slc", [](const MultiWavelength& self) { return self.indexes; });
    py::class_<Pulse, BaseSource, std::shared_ptr<Pulse>>(module, "Pulse").def(py::init<double, double, double, const py::array_t<int64_t>&>()).def("add_to_field", &Pulse::add_to_field).def_property_readonly("_slc", [](const Pulse& self) { return self.indexes; });
    py::class_<PointWaveSource, MultiWavelength, std::shared_ptr<PointWaveSource>>(module, "PointWaveSource").def(py::init<py::object, py::object, py::tuple, py::object, py::object, py::object, double>(), py::arg("grid"), py::arg("wavelength"), py::arg("position"), py::arg("amplitude"), py::arg("edgecolor") = "red", py::arg("facecolor") = "red", py::arg("alpha") = .3).def("add_to_ax", &PointWaveSource::add_to_ax).def("plot", &PointWaveSource::plot);
    py::class_<LineWaveSource, MultiWavelength, std::shared_ptr<LineWaveSource>>(module, "LineWaveSource").def(py::init<py::object, py::object, py::tuple, py::tuple, py::object, py::object, py::object, double>(), py::arg("grid"), py::arg("wavelength"), py::arg("position_0"), py::arg("position_1"), py::arg("amplitude"), py::arg("edgecolor") = "red", py::arg("facecolor") = "red", py::arg("alpha") = .3).def("add_to_ax", &LineWaveSource::add_to_ax).def("plot", &LineWaveSource::plot);
    py::class_<PointPulseSource, Pulse, std::shared_ptr<PointPulseSource>>(module, "PointPulseSource").def(py::init<py::object, double, py::object, py::tuple, py::object, py::object, py::object, double>(), py::arg("grid"), py::arg("amplitude"), py::arg("duration"), py::arg("position"), py::arg("delay") = 0., py::arg("edgecolor") = "red", py::arg("facecolor") = "red", py::arg("alpha") = .3).def("add_to_ax", &PointPulseSource::add_to_ax).def("plot", &PointPulseSource::plot);
    py::class_<LinePulseSource, Pulse, std::shared_ptr<LinePulseSource>>(module, "LinePulseSource").def(py::init<py::object, double, py::object, py::tuple, py::tuple, py::object, py::object, py::object, double>(), py::arg("grid"), py::arg("amplitude"), py::arg("duration"), py::arg("position_0"), py::arg("position_1"), py::arg("delay") = 0., py::arg("edgecolor") = "red", py::arg("facecolor") = "red", py::arg("alpha") = .3).def("add_to_ax", &LinePulseSource::add_to_ax).def("plot", &LinePulseSource::plot);
}
