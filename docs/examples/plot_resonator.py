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
    size_x=50e-6,
    size_y=30e-6,
    n_steps=800
)

experiment = Experiment(grid=grid)


scatterer = experiment.add_ring_resonator(
    position=('35%', '50%'),
    epsilon_r=1.5,
    inner_radius=4e-6,
    width=2e-6
)


# %%
# We add a line source
source = experiment.add_point_source(
    wavelength=1550e-9,
    position=('25%', '50%'),
    amplitude=100,
)

# %%
# We add a perfectly matched layer to avoid reflection at the boundary of the mesh
pml = experiment.add_pml(order=1, width=70, sigma_max=5000)

# %%
# Plotting of the whole experiemnt setup
experiment.plot()

experiment.run_fdtd()

experiment.plot_frame(frame_number=-1, scale_max=4)

animation = experiment.render_propagation(skip_frame=5, colormap=polytechnique.red_black_blue)

animation.save('./resonator.gif', writer='Pillow', fps=10)

# -
