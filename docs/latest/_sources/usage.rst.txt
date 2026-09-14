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

Keeping results from multiple runs
---------------------------------

``run()`` returns a :class:`~LightWave2D.result.SimulationResult`. Keep this
object to compare runs without copying the full field history yourself:

.. code-block:: python

   first = experiment.run(store_every=5)
   second = experiment.run(store_fields=False)
   first.plot_frame(-1)
   animation = first.render_propagation(skip_frame=1, show=False)
   signals = second.detector_data
   times = second.recorded_time_stamp

``detector_data`` has shape ``(recorded_steps, number_of_detectors)``; columns
follow detector insertion order. ``Ez_t`` has shape ``(recorded_steps, nx, ny)``
or is ``None`` in detector-only mode. Timestamps retain their units. Each run
allocates its own output arrays, so a later run does not overwrite earlier
results. Arrays remain editable; geometry overlays reference the original
configured objects rather than deep copies.

Existing ``experiment.Ez_t``, ``experiment.recorded_time_stamp``, plotting
methods, and ``detector.data`` still refer to the latest successful run.

Implementation and validation
-----------------------------

``Experiment`` configures geometry and exposes the convenience API.
``execution.py`` prepares material meshes, invokes the native solver, and
collects results. ``result.py`` stores each run's outputs, while
``visualization.py`` implements geometry plots, field plots, and animations.
The native time loop computes spatial differences directly and prepares fixed
material coefficients once per run.

The physics regression suite checks vacuum pulse speed, normal-incidence
Fresnel amplitudes, decreasing pulse error with mesh refinement, and reduced
boundary reflection. The graded-conductivity boundary benchmark currently
permits up to 30% reflected amplitude (about 25% measured for that setup).
This is a regression baseline, not a guarantee of negligible PML reflection;
check boundary convergence for your own simulation.

For a repeatable local timing comparison, run
``OMP_NUM_THREADS=1 python tools/benchmark_solver.py`` from a source checkout
before and after rebuilding. The script reports median timings for two grid
resolutions, including setup and detector recording but no field history.

Independent sampling and disk recording
--------------------------------------

``field_every`` and ``detector_every`` override ``store_every`` independently.
Point detectors and flux monitors share ``detector_every``. For dense detector
signals with sparse field frames:

.. code-block:: python

   result = experiment.run(field_every=20, detector_every=1)
   field_times = result.recorded_time_stamp
   detector_times = result.detector_time_stamp

Decimation does not apply an anti-aliasing filter. Choose the detector cadence
to resolve the highest frequency of interest; use every step when unsure.

To write field frames directly to disk:

.. code-block:: python

   from LightWave2D.result import SimulationResult

   result = experiment.run(
       field_every=20, detector_every=1, field_path="fields.npy"
   )
   reopened = SimulationResult.load_fields("fields.npy")
   reopened.plot_frame(-1)

The solver writes into a NumPy memory map, avoiding an in-memory allocation
of the entire field history. The operating system manages disk caching.
``fields.npy.metadata.npz`` stores SI coordinates and field timestamps;
it is written after successful integration and flushing. Missing metadata
indicates an incomplete recording. Existing output files are never overwritten.
Both files are needed to reopen a result. This format stores field history,
not detector signals, flux records, or geometry overlays. Animation color-limit
calculation scans one frame at a time to avoid a full-history temporary array.

Spectra and power-flux monitors
------------------------------

Point detector spectra return frequencies in Hz and complex, one-sided
electric-field amplitudes:

.. code-block:: python

   spectrum = result.detector_spectrum(0, window="hann")
   frequency = spectrum.frequency
   amplitude = spectrum.amplitude

Supported windows are ``"hann"`` and ``"boxcar"``. Scaling compensates for the
window's coherent gain. At least two samples are needed (three for Hann).
The result uses coherent electric samples even if the detector's display data
was configured as magnitude-only.

A flux monitor integrates the signed Poynting flux along an axis-aligned line.
For a source propagating in positive x, place vertical monitors upstream and
downstream of the structure, outside sources and absorbing layers:

.. code-block:: python

   from TypedUnit import ureg

   experiment.add_flux_monitor(
       position_0=("30%", "20%"), position_1=("30%", "80%"), normal=1
   )
   experiment.add_flux_monitor(
       position_0=("80%", "20%"), position_1=("80%", "80%"), normal=1
   )
   reference = experiment.run(store_fields=False, detector_every=1)

   # Add the structure of interest, keeping source and monitor settings fixed.
   experiment.add_circle(
       position=("55%", "50%"), radius=1 * ureg.micrometer, epsilon_r=4
   )
   sample = experiment.run(store_fields=False, detector_every=1)

   incident = reference.flux[0].spectrum(window="boxcar")
   reflected = sample.flux[0].spectrum(
       window="boxcar", subtract=reference.flux[0]
   )
   reflection = -reflected.normalized(incident)
   transmission = sample.flux[1].spectrum(window="boxcar").normalized(
       reference.flux[1].spectrum(window="boxcar")
   )

Reflection subtraction operates on electric and magnetic fields before forming
power. Field subtraction requires matching monitor geometry, sampling and normal. Use identical
run durations and spectral windows, and capture the complete pulse response.
Weak reference bins (below ``cutoff=1e-6`` times the largest absolute reference
power) return NaN instead of unstable ratios. Normalization assumes the
reference monitor measures the intended incident flux; finite apertures and
unwanted boundary returns affect the interpretation.

``normal=1`` points along positive x for vertical monitors and positive y for
horizontal monitors; ``normal=-1`` reverses the sign. Endpoints are snapped to
grid cells and integrated with trapezoidal weights. Lines must be at least one
cell inside grid boundaries. The native solver centers H spatially on Ez and
averages adjacent electric time steps to align with H's half-step. Flux record
timestamps therefore equal detector timestamps minus half a solver time step.

``FluxRecord.data`` has shape ``(samples, line points, 2)``. Its last axis holds
the centered electric field and signed tangential magnetic field (``-Hy`` for
vertical lines, ``Hx`` for horizontal lines). Flux spectra report W/m per unit
out-of-plane length when source amplitudes represent V/m. They are Fourier-bin
powers, not a power spectral density; pulse spectra are most useful normalized
to a matching reference run.
