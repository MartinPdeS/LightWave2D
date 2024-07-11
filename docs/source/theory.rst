Theoretical Background
=======================

Finite-Difference Time-Domain Method (FDTD)
-------------------------------------------

.. note::

  The Finite-Difference Time-Domain (FDTD) method is a numerical analysis technique used to model computational electrodynamics. It is particularly useful for solving Maxwell's equations for complex structures and media.
  LightWave2D employs the FDTD method to simulate the interaction of electromagnetic waves with various components in a two-dimensional grid. This allows for the accurate analysis of wave propagation, scattering, and diffraction.

  The FDTD method discretizes both the spatial and temporal domains. It uses central-difference approximations to Maxwell's curl equations. By stepping through time iteratively, it updates the electric and magnetic fields within the simulation grid.

.. math::
  &\frac{\partial \vec{E}}{\partial t} = \frac{1}{\epsilon} \nabla \times \vec{H} - \frac{\sigma}{\epsilon} \vec{E}
  .. &\frac{\partial \vec{H}}{\partial t} = -\frac{1}{\mu} \nabla \times \vec{E}

  .. Here, \vec{E} and \vec{H} represent the electric and magnetic fields, respectively. \epsilon and \mu are the permittivity and permeability of the medium, and \sigma is the electrical conductivity.

Component Modeling
------------------

Waveguide
---------

.. note::

  A waveguide in LightWave2D guides electromagnetic waves from one point to another with minimal loss. The waveguide's width and height can be specified in grid cells or set to 'full' to occupy the entire grid dimension.

.. math::
    &\epsilon_r(x, y) =
    \begin{cases}
        \epsilon_{r, \text{wg}} & \text{if } (x, y) \in \text{Waveguide} \\
        \epsilon_{r, \text{bg}} & \text{otherwise}
    \end{cases}

Square Scatterer
----------------

.. note::

  The square scatterer is a simple component with a uniform relative permittivity. It is defined by its center position and side length.

.. math::
  &\epsilon_r(x, y) =
  \begin{cases}
  \epsilon_{r, \text{sq}} & \text{if } (x, y) \in \text{Square} \\
  \epsilon_{r, \text{bg}} & \text{otherwise}
  \end{cases}

Circle Scatterer
----------------

.. note::

  A circular scatterer is another basic component defined by its center position and radius. It scatters incident waves uniformly.

.. math::
  &\epsilon_r(x, y) =
  \begin{cases}
  \epsilon_{r, \text{circle}} & \text{if } (x, y) \in \text{Circle} \\
  \epsilon_{r, \text{bg}} & \text{otherwise}
  \end{cases}

Ellipse Scatterer
-----------------

.. note::

  An elliptical scatterer is defined by its center position, width, height, and rotation angle. It provides an anisotropic scattering effect.

.. math::
  &\epsilon_r(x, y) =
  \begin{cases}
  \epsilon_{r, \text{ellipse}} & \text{if } (x, y) \in \text{Ellipse} \\
  \epsilon_{r, \text{bg}} & \text{otherwise}
  \end{cases}

Triangle Scatterer
------------------

.. note::

  A triangular scatterer is defined by its center position and side length. It provides a unique scattering pattern due to its geometric shape.

.. math::
  &\epsilon_r(x, y) =
  \begin{cases}
  \epsilon_{r, \text{triangle}} & \text{if } (x, y) \in \text{Triangle} \\
  \epsilon_{r, \text{bg}} & \text{otherwise}
  \end{cases}

Lense
-----

.. note::

  A lens in LightWave2D focuses or defocuses waves based on its radius of curvature and width. It can be either convex or concave.

.. math::
  &\epsilon_r(x, y) =
  \begin{cases}
  \epsilon_{r, \text{lense}} & \text{if } (x, y) \in \text{Lense} \\
  \epsilon_{r, \text{bg}} & \text{otherwise}
  \end{cases}

Grating
-------

.. note::

  A grating is used to diffract light and study diffraction patterns. It is defined by its period, duty cycle, and number of periods.

.. math::
  &\epsilon_r(x, y) =
  \begin{cases}
  \epsilon_{r, \text{grating}} & \text{if } (x, y) \in \text{Grating} \\
  \epsilon_{r, \text{bg}} & \text{otherwise}
  \end{cases}

Ring Resonator
--------------

.. note::

  A ring resonator is used to study resonant effects. It is defined by its inner and outer radius.

.. math::
  &\epsilon_r(x, y) =
  \begin{cases}
  \epsilon_{r, \text{ring}} & \text{if } (x, y) \in \text{Ring Resonator} \\
  \epsilon_{r, \text{bg}} & \text{otherwise}
  \end{cases}

Rectangular Waveguide
---------------------

.. note::

  A rectangular waveguide is used to guide electromagnetic waves with a defined width, height, and length.

.. math::
  &\epsilon_r(x, y) =
  \begin{cases}
  \epsilon_{r, \text{rect}} & \text{if } (x, y) \in \text{Rectangular Waveguide} \\
  \epsilon_{r, \text{bg}} & \text{otherwise}
  \end{cases}

