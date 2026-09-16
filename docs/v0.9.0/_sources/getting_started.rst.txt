Getting started
===============

Installation
------------

Install LightWave2D and its runtime dependencies from PyPI:

.. code-block:: bash

   python -m pip install LightWave2D

Use the documentation extra when building this site locally:

.. code-block:: bash

   python -m pip install -e ".[documentation]"
   cd docs
   make html

Your first simulation
---------------------

This complete example creates a small dielectric scatterer, injects a
continuous line source, absorbs outgoing waves with a PML, and records a
downsampled field history for plotting.

.. code-block:: python

   from TypedUnit import ureg
   from LightWave2D.experiment import Experiment
   from LightWave2D.grid import Grid

   grid = Grid(
       resolution=0.25 * ureg.micrometer,
       size_x=20 * ureg.micrometer,
       size_y=12 * ureg.micrometer,
       n_steps=300,
   )
   experiment = Experiment(grid=grid)
   experiment.add_circle(
       position=("55%", "center"),
       radius=1.5 * ureg.micrometer,
       epsilon_r=2.25,
   )
   experiment.add_line_source(
       position_0=("15%", "bottom"),
       position_1=("15%", "top"),
       wavelength=1.55 * ureg.micrometer,
       amplitude=1.0,
   )
   experiment.add_pml(width="10%", order=3)
   experiment.run(store_every=5)
   experiment.plot_frame(frame_number=-1)

All spatial inputs accept ``TypedUnit`` quantities. Position strings such as
``"center"`` and ``"25%"`` are resolved against the valid field-sample area.

Where to go next
----------------

* Read :doc:`simulation_design` before choosing a production grid.
* Read :doc:`usage` to reduce field-history memory or run detector-only jobs.
* Browse the gallery for complete scattering, detector, and photonic-component
  examples.
