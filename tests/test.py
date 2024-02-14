from LightWave2D.grid import Grid
from LightWave2D.experiment import Experiment  # get_field_propagation


grid = Grid(
    n_x=400,
    n_y=200,
    size_x=4 * 8e-6,
    size_y=4 * 4e-6,
    n_steps=2000
)

experiment = Experiment(
    grid=grid,
)

scatterer = experiment.add_scatterer(
    position=('center', 'center'),
    epsilon_r=2,
    radius=4e-6
)

# scatterer = experiment.add_scatterer(
#     position=('center', 'top'),
#     epsilon_r=2,
#     radius=1e-6
# )

# scatterer = experiment.add_scatterer(
#     position=('center', 'bottom'),
#     epsilon_r=2,
#     radius=1e-6
# )

# scatterer.plot().show()


source = experiment.add_vertical_line_source(
    wavelength=1550e-9,
    x_position=3e-6,
    amplitude=100,
    y_positions=(7e-6, 9e-6)
)

# source.plot().show()

experiment.add_pml(
    order=1,
    width=70,
    sigma_max=5000
)

detector = experiment.add_detector(
    position=('center', 'center'),
)


# experiment.plot().show()

experiment.run_fdtd()

experiment.render_propagtion()

# experiment.mpsplots_plot_propgation(dark_colormap=False)

# experiment.plot_propgation(dark_colormap=False)
