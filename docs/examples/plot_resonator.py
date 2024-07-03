"""
Experiment: Ring Resonator
==========================

This example demonstrates the setup and execution of a ring resonator experiment using LightWave2D.
We will define the simulation grid, add a ring resonator scatterer, a point source, apply a perfectly matched layer (PML), run the simulation, and visualize the results.
"""

# %%
# Importing the necessary packages
from LightWave2D.grid import Grid
from LightWave2D.experiment import Experiment
from MPSPlots.colormaps import polytechnique

# %%
# Define the simulation grid
grid = Grid(
    resolution=0.1e-6,  # Grid resolution in meters
    size_x=50e-6,       # Grid size in the x direction in meters
    size_y=30e-6,       # Grid size in the y direction in meters
    n_steps=800         # Number of time steps for the simulation
)

# Initialize the experiment with the defined grid
experiment = Experiment(grid=grid)

# %%
# Add a ring resonator scatterer to the experiment
scatterer = experiment.add_ring_resonator(
    position=('35%', '50%'),  # Center position of the ring resonator
    epsilon_r=1.5,            # Relative permittivity of the ring resonator
    inner_radius=4e-6,        # Inner radius of the ring resonator in meters
    width=2e-6                # Width of the ring resonator in meters
)

# %%
# Add a point source to the experiment
source = experiment.add_point_source(
    wavelength=1550e-9,       # Wavelength of the source in meters
    position=('25%', '50%'),  # Position of the source
    amplitude=100             # Amplitude of the source
)

# %%
# Add a perfectly matched layer (PML) to absorb boundary reflections
pml = experiment.add_pml(
    order=1,          # Order of the PML polynomial profile
    width='10%',      # Width of the PML region as a percentage of grid size
    sigma_max=5000    # Maximum conductivity for the PML
)

# %%
# Plot the entire experiment setup
experiment.plot()

# Run the FDTD simulation
experiment.run_fdtd()

# %%
# Plot the last time frame of the computed fields
experiment.plot_frame(
    frame_number=-1,  # Plot the last frame
    scale_max=4       # Maximum scale for the field visualization
)

# %%
# Render an animation of the field propagation over time
animation = experiment.render_propagation(
    skip_frame=5,                            # Number of frames to skip in the animation
    colormap=polytechnique.red_black_blue    # Colormap for the animation
)

# Save the animation as a GIF file
_ = animation.save('./ring_resonator_propagation.gif', writer='Pillow', fps=10)
