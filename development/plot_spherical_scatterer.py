"""
Experiment: Circular Scatterer
==============================

This example demonstrates the setup and execution of a circular scatterer experiment using LightWave2D.
We will define the simulation grid, add a circular scatterer and a line source, apply a perfectly matched layer (PML), run the simulation, and visualize the results.
"""

# %%
# Importing the necessary packages
from LightWave2D.grid import Grid
from LightWave2D.experiment import Experiment
from MPSPlots import colormaps

# %%
# Define the simulation grid
grid = Grid(
    resolution=0.03e-6,  # Grid resolution in meters
    size_x=50e-6,       # Grid size in the x direction in meters
    size_y=50e-6,       # Grid size in the y direction in meters
    n_steps=1600         # Number of time steps for the simulation
)

# Initialize the experiment with the defined grid
experiment = Experiment(grid=grid)

# %%
# Add a circular scatterer to the experiment
scatterer = experiment.add_circle(
    position=('50%', '50%'),  # Center position of the scatterer
    epsilon_r=1.5,            # Relative permittivity of the scatterer
    radius=0.5e-6,              # Radius of the circular scatterer in meters
    sigma=0e6
)

# %%
# Add a line source to the experiment
source = experiment.add_line_source(
    wavelength=1550e-9,         # Wavelength of the source in meters
    position_0=('30%', '55%'),  # Starting position of the source
    position_1=('30%', '45%'),  # Ending position of the source
    amplitude=10                # Amplitude of the source
)

# %%
# Add a perfectly matched layer (PML) to absorb boundary reflections
experiment.add_pml(
    order=1,          # Order of the PML polynomial profile
    width='10%',      # Width of the PML region as a percentage of grid size
    sigma_max=5000    # Maximum conductivity for the PML
)

# %%
# Plot the entire experiment setup
# experiment.plot()

# Run the FDTD simulation
experiment.run_fdtd()


experiment.save_frame_as_image(
    filename='./fdtd_1mu.png',
    frame_number=-1,  # Plot the last frame
    scale_max=1,      # Maximum scale for the field visualization
    colormap=colormaps.polytechnique.red_black_blue,  # Colormap for the plot
    dpi=600
)
