"""
Detector-only recording
=======================

Record a point-detector trace without allocating the full electric-field time
history. This is the preferred mode for transmission, reflection, and spectral
measurements on large grids.
"""

# %%
from TypedUnit import ureg

from LightWave2D.experiment import Experiment
from LightWave2D.grid import Grid


grid = Grid(
    resolution=0.25 * ureg.micrometer,
    size_x=24 * ureg.micrometer,
    size_y=12 * ureg.micrometer,
    n_steps=400,
)
experiment = Experiment(grid=grid)

experiment.add_line_source(
    position_0=("15%", "bottom"),
    position_1=("15%", "top"),
    wavelength=1.55 * ureg.micrometer,
    amplitude=1.0,
)
detector = experiment.add_point_detector(position=("75%", "center"))
experiment.add_pml(width="15%", order=3)

# %%
# Keep one sample every five solver steps. ``Ez_t`` remains ``None`` after this
# run, while the detector retains both the samples and their physical times.
experiment.run(store_fields=False, store_every=5)

detector.plot_data()
