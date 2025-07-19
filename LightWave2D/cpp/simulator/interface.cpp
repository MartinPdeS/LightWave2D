#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include "simulator.h"

namespace py = pybind11;

PYBIND11_MODULE(interface_simulator, m) {
    m.doc() = R"pbdoc(
        Python bindings for the FDTD simulation engine.

        This module provides access to a C++-based finite-difference time-domain (FDTD) simulator.
        It supports nonlinear optics (e.g., Kerr and SHG), spatially varying permittivity and conductivity,
        and time-resolved field sampling.
    )pbdoc";

    pybind11::class_<FDTDSimulator>(m, "FDTDSimulator",
        R"pbdoc(
            FDTDSimulator(config, mesh_set, sources)

            A full-featured electromagnetic FDTD solver using the Yee scheme.

            Parameters
            ----------
            config : Config
                Simulation configuration object containing global parameters like grid spacing, time step, etc.

            mesh_set : MeshSet
                Mesh structure containing spatial properties like permittivity, conductivity, and nonlinear parameters.

            sources : list of BaseSource
                List of time-dependent sources (e.g., impulsive or continuous wave) injected into the simulation domain.
        )pbdoc"
        )

        .def(
            pybind11::init<>(),
            R"pbdoc(
                Initialize an empty FDTDSimulator instance.
            )pbdoc"
        )
        .def("_cpp_set_sources",
            &FDTDSimulator::set_sources,
            pybind11::arg("sources")
        )
        .def("_cpp_set_config",
            &FDTDSimulator::set_config,
            pybind11::arg("dt"),
            pybind11::arg("dx"),
            pybind11::arg("dy"),
            pybind11::arg("nx"),
            pybind11::arg("ny"),
            pybind11::arg("time_stamp"),
            R"pbdoc(
                Set the simulation configuration parameters.

                Parameters
                ----------
                dt : float
                    Time step in seconds.
                n_steps : int
                    Total number of simulation steps to perform.
                dx : float
                    Grid spacing in the x-direction (meters).
                dy : float
                    Grid spacing in the y-direction (meters).
                nx : int
                    Number of grid points in the x-direction.
                ny : int
                    Number of grid points in the y-direction.
                time_stamp : list of float
                    A vector containing the physical time corresponding to each simulation step.
            )pbdoc"
        )
        .def("_cpp_set_geometry_mesh",
            &FDTDSimulator::set_geometry_mesh,
            pybind11::arg("epsilon"),
            pybind11::arg("n2"),
            pybind11::arg("gamma"),
            pybind11::arg("sigma_x"),
            pybind11::arg("sigma_y"),
            pybind11::arg("mu_0"),
            R"pbdoc(
                Set the geometry mesh parameters.

                Parameters
                ----------
                epsilon : numpy.ndarray
                    2D array of permittivity values at each grid point (F/m).
                n2 : numpy.ndarray
                    2D array representing the Kerr nonlinear coefficient at each point (m²/W).
                gamma : numpy.ndarray
                    2D array of absorption coefficients for nonlinear media (1/s).
                sigma_x : numpy.ndarray
                    2D array of shape (nx, ny) representing the conductivity in the x-direction (S/m).
                sigma_y : numpy.ndarray
                    2D array of shape (nx, ny) representing the conductivity in the y-direction (S/m).
                mu_0 : float
                    Magnetic permeability of free space (H/m).
            )pbdoc"
        )
        .def("_cpp_run",
            &FDTDSimulator::run,
            pybind11::arg("Ez_time"),
            R"pbdoc(
            Run the FDTD simulation for a given number of time steps.

            Parameters
            ----------
            Ez_time : numpy.ndarray
                A 3D NumPy array of shape (n_steps, nx, ny) to store the z-component of the electric field over time.

            )pbdoc"
        );
}
