#include "mesh_set.h"


MeshSet::MeshSet(
    const pybind11::array_t<double>& epsilon,
    const pybind11::array_t<double>& n2,
    const pybind11::array_t<double>& gamma,
    const double mu,
    const pybind11::array_t<double>& sigma_x,
    const pybind11::array_t<double>& sigma_y):
epsilon(epsilon), n2(n2), gamma(gamma), mu(mu), sigma_x(sigma_x), sigma_y(sigma_y)
{

}