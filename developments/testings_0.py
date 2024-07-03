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
    size_x=50e-6,
    size_y=15e-6,
    n_steps=1200
)

experiment = Experiment(grid=grid)

# scatterer = experiment.add_ellipse(
#     position=('30%', '40%'),
#     width=4e-6,
#     height=4e-6,
#     epsilon_r=1,
# )


scatterer = experiment.add_waveguide(
    position_0=('0%', '50%'),
    position_1=('100%', '50%'),
    width=2e-6,
    epsilon_r=2,
)

source = experiment.add_line_source(
    wavelength=1550e-9,
    position_0=('20%', '45%'),
    position_1=('20%', '55%'),
    amplitude=10,
)


# source = experiment.add_impulsion(
#     duration=1e-15,
#     delay=0,
#     position=('50%', '50%'),
#     amplitude=1000,
# )


# %%
# We add a perfectly matched layer to avoid reflection at the boundary of the mesh
experiment.add_pml(order=1, width='10%', sigma_max=5000)

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
    skip_frame=10,
    colormap=colormaps.polytechnique.red_black_blue,
    scale_max=2
)

_ = animation.save('./resonator.gif', writer='Pillow', fps=20)


# -
