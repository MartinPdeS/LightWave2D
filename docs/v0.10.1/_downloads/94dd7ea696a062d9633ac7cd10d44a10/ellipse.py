"""
Elliptic Scatterer
==================

This example demonstrates the setup and execution of an elliptic scatterer experiment using LightWave2D.
We will define the simulation grid, add an elliptic scatterer and a line source, apply a perfectly matched layer (PML), run the simulation, and visualize the results.
"""

# %%
from TypedUnit import ureg
from MPSPlots import colormaps

from LightWave2D.grid import Grid
from LightWave2D.experiment import Experiment

grid = Grid(
    resolution=0.1 * ureg.micrometer,
    size_x=40 * ureg.micrometer,
    size_y=30 * ureg.micrometer,
    n_steps=400,
)

experiment = Experiment(grid=grid)

scatterer = experiment.add_ellipse(
    position=("30%", "40%"),  # Center position of the ellipse
    width=4 * ureg.micrometer,
    height=10 * ureg.micrometer,
    epsilon_r=2,  # Relative permittivity of the ellipse
)

source = experiment.add_line_source(
    wavelength=1550 * ureg.nanometer,
    position_0=("10%", "100%"),  # Starting position of the source
    position_1=("10%", "0%"),  # Ending position of the source
    amplitude=10,  # Amplitude of the source
)

experiment.add_pml(
    order=1,  # Order of the PML polynomial profile
    width="10%",  # Width of the PML region as a percentage of grid size
    sigma_max=5000 * ureg.siemens / ureg.meter,  # Maximum conductivity for the PML
)

experiment.run()

animation = experiment.render_propagation(
    skip_frame=5,  # Number of frames to skip in the animation
    colormap=colormaps.polytechnique.red_black_blue,  # Colormap for the animation
    enhance_contrast=4,  # Enhance contrast for better visualization
    save_as="./elliptic_scatterer.gif",  # Save the animation as a GIF file
    fps=30,
)
