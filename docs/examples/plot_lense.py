"""
Experiment: circular scatterer
==============================

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
    size_x=60e-6,
    size_y=30e-6,
    n_steps=1200
)

experiment = Experiment(grid=grid)


# %%
# We add a circular scatterer
scatterer = experiment.add_lense(
    position=('35%', '50%'),
    epsilon_r=2,
    curvature=10e-6,
    width=5e-6
)

# %%
# We add a line source
source = experiment.add_point_source(
    wavelength=1550e-9,
    position=('10%', '50%'),
    amplitude=10,
)


# %%
# We add a perfectly matched layer to avoid reflection at the boundary of the mesh
experiment.add_pml(order=1, width='10%', sigma_max=5000)


# %%
# Plotting of the whole experiemnt setup
experiment.plot()

experiment.run_fdtd()

# %%
# Plotting the last time frame of the computed fields
experiment.plot_frame(
    frame_number=-1,
    scale_max=5,
    colormap=colormaps.polytechnique.red_black_blue
)


# %%
# Rendering animation of the field in time
animation = experiment.render_propagation(
    skip_frame=5,
    unit_size=5,
    colormap=colormaps.polytechnique.red_black_blue
)

animation.save('./lense.gif', writer='Pillow', fps=10)

# -
