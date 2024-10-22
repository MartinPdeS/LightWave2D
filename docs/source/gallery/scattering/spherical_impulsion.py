"""
Circular Scatterer
==================

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
    resolution=0.2e-6,  # Grid resolution in meters
    size_x=52e-6,       # Grid size in the x direction in meters
    size_y=40e-6,       # Grid size in the y direction in meters
    n_steps=800         # Number of time steps for the simulation
)

# Initialize the experiment with the defined grid
experiment = Experiment(grid=grid)

# %%
# Add a circular scatterer to the experiment
scatterer = experiment.add_circle(
    position=('50%', '50%'),  # Center position of the scatterer
    epsilon_r=2.5,            # Relative permittivity of the scatterer
    radius=4e-6,              # Radius of the circular scatterer in meters
    sigma=0e6
)

# %%
# Add a line source to the experiment
source = experiment.add_line_impulsion(
    duration=1e-15,         # Wavelength of the source in meters
    position_0=('30%', '60%'),  # Starting position of the source
    position_1=('30%', '40%'),  # Ending position of the source
    amplitude=1,                # Amplitude of the source
    delay=0e-14
)

# %%
# Add a perfectly matched layer (PML) to absorb boundary reflections
experiment.add_pml(
    order=1,          # Order of the PML polynomial profile
    width='20%',      # Width of the PML region as a percentage of grid size
    sigma_max=10_000    # Maximum conductivity for the PML
)

# %%
# Plot the entire experiment setup
experiment.plot()

# Run the FDTD simulation
experiment.run_fdtd()


# %%
# Render an animation of the field propagation over time
animation = experiment.show_propagation(
    skip_frame=5,                            # Number of frames to skip in the animation
    unit_size=5,                             # Size of each unit in the animation
    colormap=colormaps.polytechnique.red_black_blue,  # Colormap for the animation
    scale_max=2
)

# Save the animation as a GIF file
animation.save('./circular_scatterer_propagation.gif', writer='Pillow', fps=30)
