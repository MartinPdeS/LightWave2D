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
    n_y=400,
    size_x=4 * 8e-6,
    size_y=4 * 8e-6,
    n_steps=300
)

experiment = Experiment(
    grid=grid,
)


# # %%
# # We add a circular scatterer
# scatterer = experiment.add_scatterer(
#     position=('center', 12e-6),
#     epsilon_r=2,
#     radius=1e-6
# )

# # %%
# # We add a circular scatterer
# scatterer = experiment.add_scatterer(
#     position=('center', 20e-6),
#     epsilon_r=2,
#     radius=1e-6
# )

# %%
# We add a circular scatterer
# scatterer = experiment.add_scatterer(
#     position=('center', 16e-6),
#     epsilon_r=2,
#     radius=8e-6
# )

# scatterer = experiment.add_square_scatterer(
#     position=('center', 16e-6),
#     epsilon_r=2,
#     side_length=6e-6,
# )

scatterer = experiment.add_lens(
    position=('center', 16e-6),
    epsilon_r=2,
    radius_x=6e-6,
    radius_y=6e-6,
)


# %%
# We add a line source
source = experiment.add_vertical_line_source(
    wavelength=1550e-9,
    x_position=3e-6,
    amplitude=100,
    y_positions=(8e-6, 24e-6)
)


# %%
# We add a perfectly matched layer to avoid reflection at the boundary of the mesh
experiment.add_pml(
    order=1,
    width=70,
    sigma_max=5000
)

# %%
# We add a detector
detector = experiment.add_circular_detector(
    position=('center', 'center'),
    radius=7e-6,
)

# %%
# Plotting of the whole experiemnt setup
experiment.plot().show()
experiment.run_fdtd()

animation = experiment.render_propagation(skip_frame=5)

animation.save('./scatter_8um.gif', writer='Pillow', fps=10)

# detector.plot_data(slc=slice(-30, None, None)).show()

# -
