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
    size_x=4 * 8e-6,
    size_y=4 * 4e-6,
    n_steps=500
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


# %%
# Plotting the field measured at detector
detector.plot_data()

# %%
# Plotting the last time frame of the computed fields
experiment.plot_frame(frame_number=-1, scale_max=4)

# %%
# Rendering animation of the field in time
animation = experiment.render_propagation(skip_frame=5, colormap=polytechnique.red_black_blue)

animation.save('./test.gif', writer='Pillow', fps=10)

# -
