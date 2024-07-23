"""
Experiment: Waveguide
=====================

This example demonstrates the setup and execution of a waveguide experiment using LightWave2D.
We will define the simulation grid, add a waveguide and a line source, apply a perfectly matched layer (PML), run the simulation, and visualize the results.
"""

# %%
# Importing the necessary packages
from LightWave2D.grid import Grid
from LightWave2D.experiment import Experiment
from MPSPlots import colormaps

# %%
# Define the simulation grid
grid = Grid(
    resolution=0.1e-6,  # Grid resolution in meters
    size_x=50e-6,        # Grid size in the x direction in meters
    size_y=15e-6,        # Grid size in the y direction in meters
    n_steps=1200         # Number of time steps for the simulation
)

# Initialize the experiment with the defined grid
experiment = Experiment(grid=grid)

# %%
# Add a waveguide to the experiment
scatterer = experiment.add_waveguide(
    position_0=('0%', '50%'),    # Starting position of the waveguide
    position_1=('100%', '50%'),  # Ending position of the waveguide
    width=2e-6,                  # Width of the waveguide in meters
    epsilon_r=2                  # Relative permittivity of the waveguide
)

# Add a line source to the experiment
source = experiment.add_line_source(
    wavelength=1550e-9,         # Wavelength of the source in meters
    position_0=('20%', '45%'),  # Starting position of the source
    position_1=('20%', '55%'),  # Ending position of the source
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
# Run the FDTD simulation
experiment.run_fdtd()

# %%
# Plot the resulting electric field distribution
experiment.plot()

# %%
# Render an animation of the wave propagation
animation = experiment.render_propagation(
    skip_frame=10,                            # Number of frames to skip in the animation
    colormap=colormaps.polytechnique.red_black_blue,  # Colormap for the animation
    scale_max=2                               # Maximum scale for the field visualization
)

# Save the animation as a GIF file
_ = animation.save('./waveguide_propagation.gif', writer='Pillow', fps=20)
