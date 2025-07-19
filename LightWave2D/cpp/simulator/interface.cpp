#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "simulator.h"

PYBIND11_MODULE(interface_simulator, module) {
    module.def("run_fdtd",
        &run_fdtd,
        "Run the FDTD simulation with the given parameters.",
        py::arg("Ez"),
        py::arg("time_stamp"),
        py::arg("sigma_x"),
        py::arg("sigma_y"),
        py::arg("epsilon"),
        py::arg("gamma"),
        py::arg("n2"),
        py::arg("dt"),
        py::arg("mu_0"),
        py::arg("n_steps"),
        py::arg("dx"),
        py::arg("dy"),
        py::arg("nx"),
        py::arg("ny"),
        py::arg("sources")
    );
}