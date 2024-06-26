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
    size_x=32e-6,
    size_y=40e-6,
    n_steps=300
)

experiment = Experiment(grid=grid)


# %%
# We add a circular scatterer
scatterer = experiment.add_circle(
    position=('30%', '50%'),
    epsilon_r=2,
    radius=3e-6
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

# %%
# We add a detector
detector = experiment.add_point_detector(position=(25e-6, 'center'))

# %%
# Plotting of the whole experiemnt setup
experiment.plot()

experiment.run_fdtd()

experiment.plot_frame(
    frame_number=-1,
    colormap=colormaps.classic.red_black_blue
)


animation = experiment.render_propagation(skip_frame=5, unit_size=3)

animation.save('./test.gif', writer='Pillow', fps=10)

# -
