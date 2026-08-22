Running simulations efficiently
===============================

Choose a grid resolution that resolves the smallest relevant wavelength and
feature, then use the smallest simulation area and duration that answer the
question. The solver chooses its time step from the Courant limit.

Recording fields and detectors
------------------------------

By default, :meth:`~LightWave2D.experiment.Experiment.run` stores every field
frame. This is convenient for animations, but it uses
``n_steps * n_x * n_y * 8`` bytes for the electric-field history.

Use ``store_every`` to retain every Nth frame while recording detectors at the
same cadence:

.. code-block:: python

   experiment.add_point_detector(position=("80%", "center"))
   experiment.run(store_every=10)
   experiment.render_propagation(skip_frame=1)

For transmission, reflection, or spectral measurements, retain detector data
without storing any field frames:

.. code-block:: python

   detector = experiment.add_point_detector(position=("80%", "center"))
   experiment.run(store_fields=False, store_every=5)
   detector.plot_data()

Field plotting and animation require ``store_fields=True``. Detector samples
remain available in ``detector.data`` and their physical timestamps in
``detector.time_stamp`` in both recording modes.

Practical setup checklist
-------------------------

* Keep sources and structures away from the PML, and use enough PML cells for
  the wavelengths being absorbed.
* Start with a small grid and short run to validate geometry and detector
  placement with ``experiment.plot()``.
* Increase resolution and compare detector results before treating a result as
  converged.
* Use a pulse source when one run must reveal a broad frequency response; use a
  wave source for a single-frequency steady-state field.
