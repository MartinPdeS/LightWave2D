"""
Ring Resonator
==============

This example demonstrates the setup and execution of a ring resonator experiment using LightWave2D.
We will define the simulation grid, add a ring resonator scatterer, a point source, apply a perfectly matched layer (PML), run the simulation, and visualize the results.
"""

# %%
# Importing the necessary packages
from TypedUnit import ureg
from MPSPlots.colormaps import polytechnique

from LightWave2D.grid import Grid
from LightWave2D.experiment import Experiment

# %%
# Define the simulation grid
grid = Grid(
    resolution=0.1 * ureg.micrometer,  # Grid resolution in meters
    size_x=50 * ureg.micrometer,       # Grid size in the x direction in meters
    size_y=30 * ureg.micrometer,       # Grid size in the y direction in meters
    n_steps=200         # Number of time steps for the simulation
)

# Initialize the experiment with the defined grid
experiment = Experiment(grid=grid)

# %%
# Add a ring resonator scatterer to the experiment
ring_resonator = experiment.add_ring_resonator(
    position=('50%', '49%'),  # Center position of the ring resonator
    epsilon_r=2.,            # Relative permittivity of the ring resonator
    inner_radius=4 * ureg.micrometer,        # Inner radius of the ring resonator in meters
    width=2 * ureg.micrometer                # Width of the ring resonator in meters
)


# %%
# Add a waveguide to the experiment
ring_resonator = experiment.add_waveguide(
    position_0=('0%', '25%'),  # Center position of the ring resonator
    position_1=('100%', '25%'),  # Center position of the ring resonator
    epsilon_r=2,            # Relative permittivity of the ring resonator
    width=2 * ureg.micrometer                # Width of the ring resonator in meters
)

# %%
# Add a point source to the experiment
source = experiment.add_line_source(
    wavelength=2110 * ureg.nanometer,       # Wavelength of the source in meters
    position_0=('10%', '23%'),  # Center position of the ring resonator
    position_1=('10%', '27%'),  # Center position of the ring resonator
    amplitude=100             # Amplitude of the source
)

# %%
# Add a perfectly matched layer (PML) to absorb boundary reflections
pml = experiment.add_pml(
    order=1,          # Order of the PML polynomial profile
    width='10%',      # Width of the PML region as a percentage of grid size
    sigma_max=5000 * ureg.siemens / ureg.meter    # Maximum conductivity for the PML
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
    enhance_contrast=2       # Maximum scale for the field visualization
)

# %%
# Render an animation of the field propagation over time
animation = experiment.render_propagation(
    skip_frame=5,                            # Number of frames to skip in the animation
    colormap=polytechnique.red_black_blue    # Colormap for the animation
)

# Save the animation as a GIF file
_ = animation.save('./ring_resonator_propagation.gif', writer='Pillow', fps=10)
