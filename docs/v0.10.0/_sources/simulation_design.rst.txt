Designing a simulation
======================

Grid and resolution
-------------------

``Grid`` derives the time step from the two-dimensional Courant limit. Choose
the spatial resolution to represent both the smallest geometric feature and the
shortest wavelength in the medium. Confirm convergence by repeating the same
measurement on a finer grid; do not rely on a single resolution.

The field samples span ``0`` through ``size - resolution`` along each axis.
The position names ``left``/``right`` and ``bottom``/``top`` therefore always
resolve to valid field indexes.

Sources
-------

Use :meth:`Experiment.add_point_source <LightWave2D.experiment.Experiment.add_point_source>`
or :meth:`Experiment.add_line_source <LightWave2D.experiment.Experiment.add_line_source>`
for monochromatic excitation. Use ``add_point_pulse`` or ``add_line_pulse``
for a Gaussian time-domain pulse and broad spectral content. Keep sources away
from material interfaces and absorbing boundaries unless the boundary behavior
itself is being studied.

Materials and boundaries
------------------------

Components set relative permittivity inside their geometry. Add a PML for open
simulations and reserve enough cells between a source or scatterer and the PML
for the desired near field. Verify the setup with ``experiment.plot()`` before
running a long job.

Measurements
------------

Point detectors expose the sampled electric field in ``detector.data`` and the
corresponding physical times in ``detector.time_stamp``. Place a detector before
calling ``run``; the compiled solver samples it at the requested recording
cadence. Use the data directly for time traces or pass it to NumPy's FFT tools
for spectral analysis.
