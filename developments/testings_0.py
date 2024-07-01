"""
Experiment: elliptic scatterer
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
    resolution=0.05e-6,
    size_x=10e-6,
    size_y=10e-6,
    n_steps=400
)

experiment = Experiment(grid=grid)

# scatterer = experiment.add_ellipse(
#     position=('30%', '40%'),
#     width=4e-6,
#     height=10e-6,
#     epsilon_r=1,
# )

# source = experiment.add_point_source(
#     wavelength=1550e-9,
#     position=('50%', '50%'),
#     amplitude=10,
# )


source = experiment.add_impulsion(
    duration=1e-15,
    delay=0,
    position=('50%', '50%'),
    amplitude=1000,
)


# %%
# We add a perfectly matched layer to avoid reflection at the boundary of the mesh
# experiment.add_pml(order=1, width=70, sigma_max=5000)

experiment.run_fdtd()

experiment.plot()

# %%
# Plotting the last time frame of the computed fields
# experiment.plot_frame(
#     frame_number=-1,
#     colormap=colormaps.polytechnique.red_black_blue,
#     scale_max=1
# )


animation = experiment.render_propagation(
    skip_frame=5,
    colormap=colormaps.polytechnique.red_black_blue,
    scale_max=5
)

_ = animation.save('./resonator.gif', writer='Pillow', fps=10)


# -
