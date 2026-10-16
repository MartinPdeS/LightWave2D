"""
Broadband pulse response
========================

Excite a dielectric circle with a short pulse and measure the transmitted time
trace. Pulse sources are useful when a single simulation must cover a range of
frequencies.
"""

# %%
from TypedUnit import ureg

from LightWave2D.experiment import Experiment
from LightWave2D.grid import Grid


grid = Grid(
    resolution=0.25 * ureg.micrometer,
    size_x=28 * ureg.micrometer,
    size_y=16 * ureg.micrometer,
    n_steps=500,
)
experiment = Experiment(grid=grid)

experiment.add_circle(
    position=("55%", "center"),
    radius=1.5 * ureg.micrometer,
    epsilon_r=2.25,
)
experiment.add_line_pulse(
    position_0=("20%", "35%"),
    position_1=("20%", "65%"),
    duration=2 * ureg.femtosecond,
    delay=6 * ureg.femtosecond,
    amplitude=1.0,
)
detector = experiment.add_point_detector(position=("80%", "center"))
experiment.add_pml(width="15%", order=3)

# %%
experiment.run(store_fields=False, store_every=2)
detector.plot_data()
