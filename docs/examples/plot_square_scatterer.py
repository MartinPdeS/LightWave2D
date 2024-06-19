"""
Experiment: scattering
======================

"""

# %%
# Importing the package
from LightWave2D.grid import Grid
from LightWave2D.experiment import Experiment


# %%
# We define here the grid on which to build the experiemnt
grid = Grid(
    n_x=400,
    n_y=200,
    size_x=4 * 8e-6,
    size_y=4 * 4e-6,
    n_steps=200
)

experiment = Experiment(grid=grid)


# %%
# We add a circular scatterer
scatterer = experiment.add_square(
    position=('25%', '50%'),
    epsilon_r=2,
    side_length=5e-6
)

# %%
# We add a line source
source = experiment.add_vertical_line_source(
    wavelength=1550e-9,
    x_position=3e-6,
    amplitude=100,
    y_positions=(7e-6, 9e-6)
)


# %%
# We add a perfectly matched layer to avoid reflection at the boundary of the mesh
experiment.add_pml(order=1, width=70, sigma_max=5000)

# %%
# We add a detector
detector = experiment.add_point_detector(position=(25e-6, 'center'))

# %%
# Plotting of the whole experiemnt setup
experiment.plot().show()

experiment.run_fdtd()

animation = experiment.render_propagation(skip_frame=5)

animation.save('./test.gif', writer='Pillow', fps=10)

# -
