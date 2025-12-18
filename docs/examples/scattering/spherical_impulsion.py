"""
Circular Scatterer
==================

This example demonstrates the setup and execution of a circular scatterer experiment using LightWave2D.
We will define the simulation grid, add a circular scatterer and a line source, apply a perfectly matched layer (PML), run the simulation, and visualize the results.
"""

# %%
# Importing the necessary packages
from TypedUnit import ureg
from MPSPlots import colormaps

from LightWave2D.grid import Grid
from LightWave2D.experiment import Experiment

grid = Grid(
    resolution=0.2 * ureg.micrometer,
    size_x=52 * ureg.micrometer,
    size_y=40 * ureg.micrometer,
    n_steps=800,
)

experiment = Experiment(grid=grid)

scatterer = experiment.add_circle(
    position=("50%", "50%"),  # Center position of the scatterer
    epsilon_r=2.5,  # Relative permittivity of the scatterer
    radius=4 * ureg.micrometer,
    sigma=0 * (ureg.siemens / ureg.meter),  # Conductivity of the scatterer
)

source = experiment.add_line_impulsion(
    duration=1 * ureg.femtosecond,
    position_0=("30%", "60%"),  # Starting position of the source
    position_1=("30%", "40%"),  # Ending position of the source
    amplitude=1,  # Amplitude of the source
    delay=0 * ureg.femtosecond,
)

experiment.add_pml(
    order=1,  # Order of the PML polynomial profile
    width="20%",  # Width of the PML region as a percentage of grid size
    sigma_max=10_000 * (ureg.siemens / ureg.meter),  # Maximum conductivity for the PML
)

experiment.plot()

experiment.run()

# %%
# Render an animation of the field propagation over time
animation = experiment.render_propagation(
    skip_frame=5,  # Number of frames to skip in the animation
    colormap=colormaps.polytechnique.red_black_blue,  # Colormap for the animation
    enhance_contrast=4,  # Enhance contrast for better visualization
    save_as="./circular_scatterer_propagation.gif",  # Save the animation as a GIF file
    fps=30,
)
