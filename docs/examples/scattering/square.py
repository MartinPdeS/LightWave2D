"""
Square Scatterer
================

This example demonstrates the setup and execution of a square scatterer experiment using LightWave2D.
We will define the simulation grid, add a square scatterer and a line source, apply a perfectly matched layer (PML), run the simulation, and visualize the results.
"""

# %%
from TypedUnit import ureg
from MPSPlots.colormaps import polytechnique

from LightWave2D.grid import Grid
from LightWave2D.experiment import Experiment

grid = Grid(
    resolution=0.1 * ureg.micrometer,  # Grid resolution
    size_x=32 * ureg.micrometer,  # Grid size in the x direction
    size_y=16 * ureg.micrometer,  # Grid size in the y direction
    n_steps=500,
)

experiment = Experiment(grid=grid)

scatterer = experiment.add_square(
    position=("25%", "50%"),  # Center position of the scatterer
    epsilon_r=2,  # Relative permittivity of the scatterer
    side_length=5 * ureg.micrometer,  # Side length of the square scatterer
)

source = experiment.add_line_source(
    wavelength=1550 * ureg.nanometer,  # Wavelength of the source
    position_0=("10%", "100%"),  # Starting position of the source
    position_1=("10%", "0%"),  # Ending position of the source
    amplitude=10,  # Amplitude of the source
)

experiment.add_pml(
    order=1,  # Order of the PML polynomial profile
    width="10%",  # Width of the PML region as a percentage of grid size
    sigma_max=5000 * ureg.siemens / ureg.meter,  # Maximum conductivity for the PML
)

detector = experiment.add_point_detector(
    position=(25 * ureg.micrometer, "center")  # Position of the detector
)
experiment.plot()

experiment.run()

detector.plot_data()


# %%
# Render an frame
experiment.plot_frame(
    frame_number=-1,  # Plot the last frame
    enhance_contrast=2,  # Maximum scale for the field visualization
)

# %%
# Render an animation of the field propagation over time
animation = experiment.render_propagation(
    skip_frame=5,  # Number of frames to skip in the animation
    colormap=polytechnique.red_black_blue,  # Colormap for the animation
    enhance_contrast=8,  # Enhance contrast for better visualization
    save_as="./square_scatterer.gif",  # Save the animation as a GIF file
    fps=30,
)
