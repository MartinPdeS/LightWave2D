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
from TypedUnit import ureg

# %%
# Define the simulation grid
grid = Grid(
    resolution=0.03 * ureg.micrometer,
    size_x=32 * ureg.micrometer,
    size_y=20 * ureg.micrometer,
    n_steps=200,
)

# Initialize the experiment with the defined grid
experiment = Experiment(grid=grid)

# %%
# Add a circular scatterer to the experiment
scatterer = experiment.add_circle(
    position=("30%", "50%"),  # Center position of the scatterer
    epsilon_r=1.5,  # Relative permittivity of the scatterer
    radius=3 * ureg.micrometer,
    sigma=0 * (ureg.siemens / ureg.meter),  # Conductivity of the scatterer
)

# %%
# Add a line source to the experiment
source = experiment.add_line_source(
    wavelength=1550 * ureg.nanometer,
    position_0=("10%", "80%"),  # Starting position of the source
    position_1=("10%", "20%"),  # Ending position of the source
    amplitude=10,  # Amplitude of the source
)

# %%
# Add a perfectly matched layer (PML) to absorb boundary reflections
experiment.add_pml(
    order=1,  # Order of the PML polynomial profile
    width="10%",  # Width of the PML region as a percentage of grid size
    sigma_max=5000 * (ureg.siemens / ureg.meter),  # Maximum conductivity for the PML
)

# %%
# Plot the entire experiment setup
experiment.plot()

# Run the FDTD simulation
experiment.run()

# %%
# Plot the last time frame of the computed fields
experiment.plot_frame(
    frame_number=-1,  # Plot the last frame
    enhance_contrast=1,  # Maximum scale for the field visualization
    colormap=colormaps.polytechnique.red_black_blue,  # Colormap for the plot
    show_intensity=True,
)

# %%
# Render an animation of the field propagation over time
animation = experiment.render_propagation(
    skip_frame=5,  # Number of frames to skip in the animation
    colormap=colormaps.polytechnique.red_black_blue,  # Colormap for the animation
    enhance_contrast=3,  # Enhance contrast for better visualization
    save_as="./circular_scatterer.gif",  # Save the animation as a GIF file
    fps=30,
)
