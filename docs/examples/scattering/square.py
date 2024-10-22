"""
Experiment: Square Scatterer
============================

This example demonstrates the setup and execution of a square scatterer experiment using LightWave2D.
We will define the simulation grid, add a square scatterer and a line source, apply a perfectly matched layer (PML), run the simulation, and visualize the results.
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
    size_x=4 * 8e-6,    # Grid size in the x direction in meters
    size_y=4 * 4e-6,    # Grid size in the y direction in meters
    n_steps=500         # Number of time steps for the simulation
)

# Initialize the experiment with the defined grid
experiment = Experiment(grid=grid)

# %%
# Add a square scatterer to the experiment
scatterer = experiment.add_square(
    position=('25%', '50%'),  # Center position of the scatterer
    epsilon_r=2,              # Relative permittivity of the scatterer
    side_length=5e-6          # Side length of the square scatterer in meters
)

# %%
# Add a line source to the experiment
source = experiment.add_line_source(
    wavelength=1550e-9,       # Wavelength of the source in meters
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

# %%
# Add a point detector to the experiment
detector = experiment.add_point_detector(
    position=(25e-6, 'center')  # Position of the detector
)

# %%
# Plot the entire experiment setup
experiment.plot()

# Run the FDTD simulation
experiment.run_fdtd()

# %%
# Plot the field measured at the detector
detector.plot_data()

# %%
# Plot the last time frame of the computed fields
experiment.plot_frame(
    frame_number=-1,  # Plot the last frame
    scale_max=2       # Maximum scale for the field visualization
)

# %%
# Render an animation of the field propagation over time
animation = experiment.render_propagation(
    skip_frame=5,                            # Number of frames to skip in the animation
    colormap=polytechnique.red_black_blue    # Colormap for the animation
)

# Save the animation as a GIF file
animation.save('./square_scatterer_propagation.gif', fps=10)
