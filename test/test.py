from LightWave2D.grid import Grid
from LightWave2D.propagation import Experiment  # get_field_propagation


grid = Grid(
    n_x=400,
    n_y=200,
    size_x=4 * 8e-6,
    size_y=4 * 4e-6,
    n_steps=3000
)

experiment = Experiment(
    grid=grid,
)

scatterer = experiment.add_scatterer(
    position=('center', 'center'),
    epsilon_r=2,
    radius=1e-6
)


source = experiment.add_vertical_line_source(
    wavelength=15500e-9,
    x_position=1e-6,
    amplitude=0.1,
    y_positions=(7e-6, 9e-6)
)

source.plot().show()

experiment.add_pml(
    order=1,
    width=70,
    sigma_max=5000
)

experiment.plot().show()

experiment.propagate()

experiment.plot_propgation()
