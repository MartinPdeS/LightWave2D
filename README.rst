LightWave2D
===========

|python|
|docs|
|PyPi|
|PyPi_download|


LightWave2D is a software designed for comprehensive 2D Finite-Difference Time-Domain (FDTD) simulations, featuring a user-friendly installation and operation process. The characterization of wave propagation, scattering, and diffraction within LightWave2D is determined by a set of specific components, as illustrated in the subsequent figure.

LightWave2D integrates various components, including waveguides, scatterers (squares, circles, ellipses, triangles, lenses), gratings, and resonators. Additional parameters governing the simulation are contingent upon the attributes of the components and the simulation setup.


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


Coding examples
***************


LightWave2D was developed with the aim of being an intuitive and easy to use tool.
Below are two examples that illustrate this:

# Spherical scatterer

.. code:: python

   from LightWave2D.grid import Grid
   from LightWave2D.experiment import Experiment
   from MPSPlots import colormaps

   grid = Grid(
       resolution=0.1e-6,
       size_x=32e-6,
       size_y=20e-6,
       n_steps=300
   )

   experiment = Experiment(grid=grid)

   scatterer = experiment.add_circle(
       position=('30%', '50%'),
       epsilon_r=2,
       radius=3e-6
   )

   source = experiment.add_line_source(
       wavelength=1550e-9,
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
       resolution=0.1e-6,
       size_x=50e-6,
       size_y=30e-6,
       n_steps=800
   )

   experiment = Experiment(grid=grid)


   scatterer = experiment.add_ring_resonator(
       position=('35%', '50%'),
       epsilon_r=1.5,
       inner_radius=4e-6,
       width=2e-6
   )

   source = experiment.add_point_source(
       wavelength=1550e-9,
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
       resolution=0.1e-6,
       size_x=60e-6,
       size_y=30e-6,
       n_steps=1200
   )

   experiment = Experiment(grid=grid)

   scatterer = experiment.add_lense(
       position=('35%', '50%'),
       epsilon_r=2,
       curvature=10e-6,
       width=5e-6
   )

   source = experiment.add_point_source(
       wavelength=1550e-9,
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

To test localy (with cloning the GitHub repository) you'll need to install the dependencies and run the coverage command as

.. code:: python

   >>> git clone https://github.com/MartinPdeS/LightWave2D.git
   >>> cd LightWave2D
   >>> pip install -r requirements/requirements.txt
   >>> coverage run --source=LightWave2D --module pytest --verbose tests
   >>> coverage report --show-missing


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

.. |docs| image:: https://readthedocs.org/projects/lightwave2d/badge/?version=latest
   :target: https://lightwave2d.readthedocs.io/en/latest/
   :alt: Documentation Status

.. |PyPi| image:: https://badge.fury.io/py/LightWave2D.svg
   :target: https://pypi.org/project/LightWave2D/

.. |PyPi_download| image:: https://img.shields.io/pypi/dm/lightwave2d.svg
   :target: https://pypistats.org/packages/lightwave2d