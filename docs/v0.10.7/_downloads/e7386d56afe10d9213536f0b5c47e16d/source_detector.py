"""
Field-history detector trace
============================

Record a point-detector trace while retaining the field history. The example's
single outcome is the detector signal; use ``detector_only.py`` when field
frames are not needed.
"""

# %%
# Importing the necessary packages
from TypedUnit import ureg

from LightWave2D.grid import Grid
from LightWave2D.experiment import Experiment

# %%
# Define the simulation grid
grid = Grid(
    resolution=0.1 * ureg.micrometer,
    size_x=60 * ureg.micrometer,
    size_y=30 * ureg.micrometer,
    n_steps=300,
)

# Initialize the experiment with the defined grid
experiment = Experiment(grid=grid)

# %%
# Add a point source to the experiment
source = experiment.add_point_source(
    wavelength=[1310] * ureg.nanometer,
    position=("10%", "50%"),  # Position of the source
    amplitude=10e10,  # Amplitude of the source
)

# %%
# Add a point detector to the experiment
detector = experiment.add_point_detector(
    position=("40%", "50%")  # Position of the detector
)

# %%
# Add a perfectly matched layer (PML) to absorb boundary reflections
experiment.add_pml(
    order=1,  # Order of the PML polynomial profile
    width="10%",  # Width of the PML region as a percentage of grid size
    sigma_max=5000 * (ureg.siemens / ureg.meter),  # Maximum conductivity for the PML
)

# %%
# Retain the field history while acquiring the detector trace.
experiment.run()

# %%
# The detector signal is the only result shown on this page.
detector.plot_data()
