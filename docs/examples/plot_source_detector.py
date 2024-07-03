"""
Experiment: Source-Detector
===========================

This example demonstrates the setup and execution of a source-detector experiment using LightWave2D.
We will define the simulation grid, add a lens scatterer, a point source, and a point detector, apply a perfectly matched layer (PML), run the simulation, and visualize the results.
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
    size_x=60e-6,       # Grid size in the x direction in meters
    size_y=30e-6,       # Grid size in the y direction in meters
    n_steps=500         # Number of time steps for the simulation
)

# Initialize the experiment with the defined grid
experiment = Experiment(grid=grid)

# %%
# Add a lens scatterer to the experiment
scatterer = experiment.add_lense(
    position=('35%', '50%'),  # Center position of the lens
    epsilon_r=2,              # Relative permittivity of the lens
    curvature=10e-6,          # Curvature of the lens in meters
    width=5e-6                # Width of the lens in meters
)

# %%
# Add a point source to the experiment
source = experiment.add_point_source(
    wavelength=[1310e-9, 1550e-9],  # Wavelengths of the source in meters
    position=('10%', '50%'),        # Position of the source
    amplitude=10                    # Amplitude of the source
)

# %%
# Add a point detector to the experiment
detector = experiment.add_point_detector(
    position=('60%', '50%')  # Position of the detector
)

# %%
# Plot the entire experiment setup
experiment.plot()

# Run the FDTD simulation
experiment.run_fdtd()

# Plot the field measured at the detector
detector.plot_data()

# %%
# Plot the last time frame of the computed fields
experiment.plot_frame(
    frame_number=-1,  # Plot the last frame
    scale_max=5,      # Maximum scale for the field visualization
    colormap=colormaps.polytechnique.red_black_blue  # Colormap for the plot
)

# %%
# Render an animation of the field propagation over time
animation = experiment.render_propagation(
    skip_frame=5,                            # Number of frames to skip in the animation
    unit_size=5,                             # Size of each unit in the animation
    colormap=colormaps.polytechnique.red_black_blue  # Colormap for the animation
)

# Save the animation as a GIF file
animation.save('./lens_propagation.gif', writer='Pillow', fps=10)
