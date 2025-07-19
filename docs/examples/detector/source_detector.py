"""
Source-Detector
===============

This example demonstrates the setup and execution of a source-detector experiment using LightWave2D.
We will define the simulation grid, add a lens scatterer, a point source, and a point detector, apply a perfectly matched layer (PML), run the simulation, and visualize the results.
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
    size_x=60 * units.micrometer,
    size_y=30 * units.micrometer,
    n_steps=100
)

# Initialize the experiment with the defined grid
experiment = Experiment(grid=grid)

# %%
# Add a lens scatterer to the experiment
scatterer = experiment.add_lense(
    position=('35%', '50%'),  # Center position of the lens
    epsilon_r=2,              # Relative permittivity of the lens
    curvature=10 * units.micrometer,
    width=5 * units.micrometer
)

# %%
# Add a point source to the experiment
source = experiment.add_point_source(
    wavelength=[1310 * units.nanometer],
    position=('10%', '50%'),        # Position of the source
    amplitude=10e10                    # Amplitude of the source
)

# %%
# Add a point detector to the experiment
detector = experiment.add_point_detector(
    position=('60%', '50%')  # Position of the detector
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
experiment.plot()

# Run the FDTD simulation
experiment.run_fdtd()

# Plot the field measured at the detector
detector.plot_data()

# %%
# Plot the last time frame of the computed fields
experiment.plot_frame(
    frame_number=-1,  # Plot the last frame
    scale_max=3,      # Maximum scale for the field visualization
    colormap=colormaps.polytechnique.red_black_blue  # Colormap for the plot
)

# %%
# Render an animation of the field propagation over time
animation = experiment.render_propagation(
    skip_frame=5,                            # Number of frames to skip in the animation
    unit_size=5,                             # Size of each unit in the animation
    colormap=colormaps.polytechnique.red_black_blue,  # Colormap for the animation
    scale_max=3
)

# Save the animation as a GIF file
animation.save('./lens_propagation.gif', writer='Pillow', fps=10)
