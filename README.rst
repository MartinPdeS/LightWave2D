LightWave2D
===========

.. list-table::
   :widths: 10 25 25
   :header-rows: 0

   * - Meta
     - |python|
     - |docs|
   * - Testing
     - |ci/cd|
     - |coverage|
   * - PyPi
     - |PyPi|
     - |PyPi_download|
   * - Anaconda
     - |anaconda|
     - |anaconda_download|



LightWave2D is a software designed for comprehensive 2D Finite-Difference Time-Domain (FDTD) simulations, featuring a user-friendly installation and operation process. The characterization of wave propagation, scattering, and diffraction within LightWave2D is determined by a set of specific components, as illustrated in the subsequent figure.

LightWave2D integrates various components, including waveguides, scatterers  (squares, circles, ellipses, triangles, lenses), gratings, and resonators. Additional parameters governing the simulation are contingent upon the attributes of the components and the simulation setup.

Key Features
************

- Intuitive API for configuring simulations.
- Support for waveguides, scatterers, gratings, and resonators.
- Built-in tools for rendering field animations.
- Extensive gallery of examples in the documentation.



----

Documentation
**************
All the latest available documentation is available `here <https://lightwave2d.readthedocs.io/en/latest/>`_ or you can click the following badge:

|docs|


----

Installation
************

For common versions of Windows, Linux, and macOS, (on x86_64 architecture), the package can readily be installed using pip;

.. code-block:: python

   >>> pip install LightWave2D

Building Documentation Locally
******************************

To generate the HTML documentation on your machine, install the optional dependencies and run:

.. code-block:: bash

   pip install .[documentation]
   cd docs && make html
   firefox build/html/index.html


Coding examples
***************


LightWave2D was developed with the aim of being an intuitive and easy to use tool.
All dimensional arguments can now be provided using `pint` quantities or strings with units.
Below are two examples that illustrate this:

# Spherical scatterer

.. code:: python

    from LightWave2D.grid import Grid
    from LightWave2D.experiment import Experiment
    from MPSPlots import colormaps
    import LightWave2D.units as units

    grid = Grid(
        resolution=0.1 * units.micrometer,
        size_x=32 * units.micrometer,
        size_y=20 * units.micrometer,
        n_steps=300
    )

   experiment = Experiment(grid=grid)

    scatterer = experiment.add_circle(
        position=('30%', '50%'),
        epsilon_r=2,
        radius=3 * units.micrometer
    )

    source = experiment.add_line_source(
        wavelength=1550 * units.nanometer,
        point_0=('10%', '100%'),
        point_1=('10%', '0%'),
        amplitude=10,
    )

   experiment.add_pml(order=1, width=70, sigma_max=5000)

   experiment.run_fdtd()

   animation = experiment.render_propagation(
       skip_frame=5,
       unit_size=5,
       colormap=colormaps.polytechnique.red_black_blue
   )

   animation.save('./spherical_scatterer.gif', writer='Pillow', fps=10)


|example_scatterer|


# Ring resonator


.. code:: python

   from LightWave2D.grid import Grid
   from LightWave2D.experiment import Experiment
   from MPSPlots.colormaps import polytechnique

    grid = Grid(
        resolution=0.1 * units.micrometer,
        size_x=50 * units.micrometer,
        size_y=30 * units.micrometer,
        n_steps=800
    )

   experiment = Experiment(grid=grid)


    scatterer = experiment.add_ring_resonator(
        position=('35%', '50%'),
        epsilon_r=1.5,
        inner_radius=4 * units.micrometer,
        width=2 * units.micrometer
    )

    source = experiment.add_point_source(
        wavelength=1550 * units.nanometer,
        position=('25%', '50%'),
        amplitude=100,
    )

   pml = experiment.add_pml(order=1, width=70, sigma_max=5000)

   experiment.run_fdtd()

   animation = experiment.render_propagation(skip_frame=5, colormap=polytechnique.red_black_blue)

   animation.save('./resonator.gif', writer='Pillow', fps=10)


|example_resonator|


# Ring resonator


.. code:: python

   from LightWave2D.grid import Grid
   from LightWave2D.experiment import Experiment
   from MPSPlots import colormaps

    grid = Grid(
        resolution=0.1 * units.micrometer,
        size_x=60 * units.micrometer,
        size_y=30 * units.micrometer,
        n_steps=1200
    )

   experiment = Experiment(grid=grid)

    scatterer = experiment.add_lense(
        position=('35%', '50%'),
        epsilon_r=2,
        curvature=10 * units.micrometer,
        width=5 * units.micrometer
    )

    source = experiment.add_point_source(
        wavelength=1550 * units.nanometer,
        position=('10%', '50%'),
        amplitude=10,
    )


   experiment.add_pml(order=1, width=50, sigma_max=5000)

   experiment.run_fdtd()

   experiment.plot_frame(
       frame_number=-1,
       scale_max=5,
       colormap=colormaps.polytechnique.red_black_blue
   )

   animation = experiment.render_propagation(
       skip_frame=5,
       unit_size=5,
       colormap=colormaps.polytechnique.red_black_blue
   )

   animation.save('./lense.gif', writer='Pillow', fps=10)


|example_lense|

Plenty of other examples are available online, I invite you to check the `examples <https://lightwave2d.readthedocs.io/en/master/gallery/index.html>`_
section of the documentation.


Testing
*******

To test locally (with cloning the GitHub repository) you'll need to install the dependencies and run the coverage command as

.. code:: python

   >>> git clone https://github.com/MartinPdeS/LightWave2D.git
   >>> cd LightWave2D
   >>> pip install -r requirements/requirements.txt
   >>> coverage run --source=LightWave2D --module pytest --verbose tests
   >>> coverage report --show-missing

Contributing
************

Contributions are welcome! Feel free to open an issue or submit a pull request on GitHub.


----

Contact Information
*******************

As of 2024 the project is still under development if you want to collaborate it would be a pleasure. I encourage you to contact me.

LightWave2D was written by `Martin Poinsinet de Sivry-Houle <https://github.com/MartinPdS>`_  .

Email:`martin.poinsinet-de-sivry@polymtl.ca <mailto:martin.poinsinet-de-sivry@polymtl.ca?subject=LightWave2D>`_ .



.. |example_resonator| image:: https://github.com/MartinPdeS/LightWave2D/blob/master/docs/images/resonator.gif?raw=true
   :alt: some image
   :class: with-shadow float-left
   :width: 800px

.. |example_lense| image:: https://github.com/MartinPdeS/LightWave2D/blob/master/docs/images/lense.gif?raw=true
   :alt: some image
   :class: with-shadow float-left
   :width: 800px

.. |example_scatterer| image:: https://github.com/MartinPdeS/LightWave2D/blob/master/docs/images/spherical_scatterer.gif?raw=true
   :alt: some image
   :class: with-shadow float-left
   :width: 800px

.. |python| image:: https://img.shields.io/badge/Made%20with-Python-1f425f.svg
   :target: https://www.python.org/

.. |docs| image:: https://github.com/martinpdes/LightWave2D/actions/workflows/deploy_documentation.yml/badge.svg
   :target: https://lightwave2d.readthedocs.io/en/latest/code.html
   :alt: Documentation Status

.. |coverage| image:: https://raw.githubusercontent.com/MartinPdeS/LightWave2D/python-coverage-comment-action-data/badge.svg
   :alt: Unittest coverage
   :target: https://htmlpreview.github.io/?https://github.com/MartinPdeS/LightWave2D/blob/python-coverage-comment-action-data/htmlcov/index.html

.. |PyPi| image:: https://badge.fury.io/py/LightWave2D.svg
   :target: https://pypi.org/project/LightWave2D/

.. |PyPi_download| image:: https://img.shields.io/pypi/dm/lightwave2d.svg
   :target: https://pypistats.org/packages/lightwave2d

.. |ci/cd| image:: https://github.com/martinpdes/lightwave2d/actions/workflows/deploy_coverage.yml/badge.svg
    :alt: Unittest Status
    :target: https://martinpdes.github.io/LightWave2D/actions

.. |anaconda| image:: https://anaconda.org/martinpdes/lightwave2d/badges/version.svg
   :alt: Anaconda version
   :target: https://anaconda.org/martinpdes/lightwave2d

.. |anaconda_download| image:: https://anaconda.org/martinpdes/lightwave2d/badges/downloads.svg
   :alt: Anaconda downloads
   :target: https://anaconda.org/martinpdes/lightwave2d
