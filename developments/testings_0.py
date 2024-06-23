"""
Experiment: scattering
======================

"""

# %%
# Importing the package
from LightWave2D.grid import Grid
from LightWave2D.experiment import Experiment
from MPSPlots.colormaps import polytechnique

# %%
# We define here the grid on which to build the experiemnt
grid = Grid(
    resolution=0.1e-6,
    size_x=30e-6,
    size_y=30e-6,
    n_steps=500
)

experiment = Experiment(grid=grid)


# %%
# We add a circular scatterer
scatterer = experiment.add_square(
    position=('25%', '20%'),
    epsilon_r=2,
    side_length=3e-6
)

# scatterer.plot()

# %%
# We add a circular scatterer
scatterer = experiment.add_ellipse(
    position=('25%', '70%'),
    epsilon_r=2,
    width=5e-6,
    height=10e-6,
    angle=10
)

# scatterer.plot()

# %%
# We add a line source
source = experiment.add_point_source(
    wavelength=1550e-9,
    position=('30%', '70%'),
    amplitude=10,
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
pml = experiment.add_pml(order=1, width=70, sigma_max=5000)
# pml.plot()


# %%
# We add a detector
detector = experiment.add_point_detector(position=(25e-6, 'center'))

# %%
# Plotting of the whole experiemnt setup
experiment.plot()

experiment.run_fdtd()

# experiment.plot_frame(frame_number=-1)

animation = experiment.render_propagation(skip_frame=5, colormap=polytechnique.red_black_blue)

animation.save('./tests.gif', writer='Pillow', fps=10)

# -
