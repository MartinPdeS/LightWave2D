"""
Experiment: scattering
======================

"""

# %%
# Importing the package
from LightWave2D.grid import Grid
from LightWave2D.experiment import Experiment
from MPSPlots import colormaps


# %%
# We define here the grid on which to build the experiemnt
grid = Grid(
    resolution=0.1e-6,
    size_x=40e-6,
    size_y=30e-6,
    n_steps=1200
)

experiment = Experiment(grid=grid)


# %%
# We add a circular scatterer
scatterer = experiment.add_circle(
    position=('30%', '40%'),
    radius=2e-6,
    epsilon_r=2,
)


scatterer = experiment.add_circle(
    position=('30%', '50%'),
    radius=2e-6,
    epsilon_r=2,
)


scatterer = experiment.add_circle(
    position=('30%', '60%'),
    radius=2e-6,
    epsilon_r=2,
)

# %%
# We add a line source
source = experiment.add_line_source(
    wavelength=1550e-9,
    point_0=('10%', '100%'),
    point_1=('10%', '0%'),
    amplitude=10,
)


# %%
# We add a perfectly matched layer to avoid reflection at the boundary of the mesh
experiment.add_pml(order=1, width=70, sigma_max=5000)

experiment.run_fdtd()

experiment.plot()

# %%
# Plotting the last time frame of the computed fields
experiment.plot_frame(
    frame_number=-1,
    colormap=colormaps.polytechnique.red_black_blue
)


# %%
# Rendering animation of the field in time
experiment.save_frame_as_image(frame_number=-1, filename='test.png')


# -
