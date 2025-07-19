"""
Elliptic Scatterer
==================

This example demonstrates the setup and execution of an elliptic scatterer experiment using LightWave2D.
We will define the simulation grid, add an elliptic scatterer and a line source, apply a perfectly matched layer (PML), run the simulation, and visualize the results.
"""

# %%
# Importing the necessary packages
from LightWave2D.grid import Grid
from LightWave2D.experiment import Experiment
from MPSPlots import colormaps
import LightWave2D.units as units

# %%
# Define the simulation grid
grid = Grid(
    resolution=0.1 * units.micrometer,
    size_x=40 * units.micrometer,
    size_y=30 * units.micrometer,
    n_steps=100
)

# Initialize the experiment with the defined grid
experiment = Experiment(grid=grid)

# %%
# Add an elliptic scatterer to the experiment
scatterer = experiment.add_ellipse(
    position=('30%', '40%'),  # Center position of the ellipse
    width=4 * units.micrometer,
    height=10 * units.micrometer,
    epsilon_r=2               # Relative permittivity of the ellipse
)

# %%
# Add a line source to the experiment
source = experiment.add_line_source(
    wavelength=1550 * units.nanometer,
    position_0=('10%', '100%'),  # Starting position of the source
    position_1=('10%', '0%'),    # Ending position of the source
    amplitude=10              # Amplitude of the source
)

# %%
# Add a perfectly matched layer (PML) to absorb boundary reflections
experiment.add_pml(
    order=1,          # Order of the PML polynomial profile
    width='10%',      # Width of the PML region as a percentage of grid size
    sigma_max=5000    # Maximum conductivity for the PML
)

# Run the FDTD simulation
experiment.run_fdtd()

# Plot the entire experiment setup
experiment.plot()

# %%
# Plot the last time frame of the computed fields
experiment.plot_frame(
    frame_number=-1,  # Plot the last frame
    colormap=colormaps.polytechnique.red_black_blue  # Colormap for the plot
)

# %%
# Save the last time frame as an image
experiment.save_frame_as_image(
    frame_number=-1,  # Frame number to save
    filename='elliptic_scatterer_last_frame.png'  # Filename for the image
)

# %%
# Render an animation of the field propagation over time
animation = experiment.render_propagation(
    skip_frame=5,                            # Number of frames to skip in the animation
    unit_size=5,                             # Size of each unit in the animation
    colormap=colormaps.polytechnique.red_black_blue  # Colormap for the animation
)

# Save the animation as a GIF file
animation.save('./elliptic_scatterer_propagation.gif', writer='Pillow', fps=10)
