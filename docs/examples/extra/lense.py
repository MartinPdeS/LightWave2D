"""
Circular Scatterer
==================

This example demonstrates the setup and execution of a circular scatterer experiment using LightWave2D.
We will define the simulation grid, add a lens scatterer, a point source, apply a perfectly matched layer (PML), run the simulation, and visualize the results.
"""

# %%
# Importing the necessary packages
from LightWave2D.grid import Grid
from LightWave2D.experiment import Experiment
from MPSPlots import colormaps
from LightWave2D import units

# %%
# Define the simulation grid
grid = Grid(
    resolution=0.1 * units.micrometer,  # Grid resolution in meters
    size_x=60 * units.micrometer,       # Grid size in the x direction in meters
    size_y=30 * units.micrometer,       # Grid size in the y direction in meters
    n_steps=100        # Number of time steps for the simulation
)

# Initialize the experiment with the defined grid
experiment = Experiment(grid=grid)


# %%
# Add a lens scatterer to the experiment
scatterer = experiment.add_lense(
    position=('35%', '50%'),  # Center position of the lens
    epsilon_r=2,              # Relative permittivity of the lens
    curvature=10 * units.micrometer,          # Curvature of the lens in meters
    width=5 * units.micrometer                # Width of the lens in meters
)

# %%
# Add a point source to the experiment
source = experiment.add_point_source(
    wavelength=1550 * units.nanometer,       # Wavelength of the source in meters
    position=('10%', '50%'),  # Position of the source
    amplitude=10              # Amplitude of the source
)

# %%
# Add a perfectly matched layer (PML) to absorb boundary reflections
experiment.add_pml(
    order=1,          # Order of the PML polynomial profile
    width='10%',      # Width of the PML region as a percentage of grid size
    sigma_max=500 * (units.siemens / units.meter)    # Maximum conductivity for the PML
)


# %%
# Plot the experiment layout
experiment.plot()


# Run the FDTD simulation
experiment.run()


# %%
# Plot the last time frame of the computed fields
experiment.plot_frame(
    frame_number=-1,  # Plot the last frame
    enhance_contrast=2,      # Maximum scale for the field visualization
    colormap=colormaps.polytechnique.red_black_blue  # Colormap for the plot
)


# %%
# Render an animation of the field propagation over time
animation = experiment.show_propagation(
    skip_frame=5,                            # Number of frames to skip in the animation
    unit_size=5,                             # Size of each unit in the animation
    colormap=colormaps.polytechnique.red_black_blue  # Colormap for the animation
)


# Save the animation as a GIF file
animation.save('./lens_propagation.gif', writer='Pillow', fps=10)
