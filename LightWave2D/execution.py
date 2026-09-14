"""Preparation and execution of a configured experiment using the native solver."""

import logging
from pathlib import Path
from LightWave2D.monitors import FluxRecord
import numpy
from LightWave2D.physics import Physics
from LightWave2D.result import SimulationResult

LOGGER = logging.getLogger(__name__)


def run(
    self,
    *,
    store_fields: bool = True,
    store_every: int = 1,
    field_every=None,
    detector_every=None,
    field_path=None,
) -> SimulationResult:
    r"""
    Run the Finite-Difference Time-Domain (FDTD) simulation.

    This method updates the electric field (Ez) and magnetic fields (Hx, Hy) over time
    based on Maxwell's equations using the FDTD method. It incorporates the effects
    of absorption, sources, and non-linear interactions.

    Maxwell's equations in 2D for non-magnetic media:

    .. math::
        \frac{\partial H_x}{\partial t} = -\frac{1}{\mu} \frac{\partial E_z}{\partial y} \\[10pt]
        \frac{\partial H_y}{\partial t} = \frac{1}{\mu} \frac{\partial E_z}{\partial x} \\[10pt]
        \frac{\partial E_z}{\partial t} = \frac{1}{\epsilon} \left( \frac{\partial H_y}{\partial x} - \frac{\partial H_x}{\partial y} \right) - \sigma E_z

    Parameters
    ----------
    store_fields : bool, optional
        Store electric-field frames for plotting and animation. Disable this
        for detector-only simulations to avoid allocating a 3D time history.
    store_every : int, optional
        Default recording cadence for fields, point detectors and flux monitors.
    field_every : int, optional
        Override the field recording cadence independently.
    detector_every : int, optional
        Override the point-detector and flux-monitor recording cadence.
    field_path : str or pathlib.Path, optional
        Write field frames to a new memory-mapped .npy file. A companion
        .npy.metadata.npz file stores timestamps and coordinates on completion.
        Requires store_fields=True. Existing files are never overwritten.

    Notes
    -----
    The full field history uses ``n_frames * n_x * n_y * 8`` bytes. Use
    ``store_every`` to reduce it, or ``store_fields=False`` for detector-only
    simulations.
    """

    def interval(value, name):
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise ValueError(f"{name} must be a positive integer.")
        return value

    interval(store_every, "store_every")
    field_every = interval(
        store_every if field_every is None else field_every, "field_every"
    )
    detector_every = interval(
        store_every if detector_every is None else detector_every, "detector_every"
    )
    if field_path is not None:
        field_path = Path(field_path).resolve()
        if not store_fields:
            raise ValueError("field_path requires store_fields=True.")
        if field_path.suffix != ".npy":
            raise ValueError("field_path must end in .npy.")
        if field_path.exists() or Path(str(field_path) + ".metadata.npz").exists():
            raise FileExistsError(
                f"Refusing to overwrite recorded fields: {field_path}"
            )

    recorded_steps = numpy.arange(0, self.grid.n_steps, field_every)
    detector_steps = numpy.arange(0, self.grid.n_steps, detector_every)
    n_recorded_steps = len(recorded_steps)
    detector_data = numpy.empty((len(detector_steps), len(self.detectors)))
    detector_indexes = numpy.asarray(
        [[detector.p0.x_index, detector.p0.y_index] for detector in self.detectors],
        dtype=numpy.int64,
    ).reshape((-1, 2))

    LOGGER.debug(
        "Preparing FDTD run: grid=%s, steps=%d, stored_frames=%d, sources=%d, detectors=%d, components=%d",
        self.grid.shape,
        self.grid.n_steps,
        n_recorded_steps,
        len(self.sources),
        len(self.detectors),
        len(self.components),
    )

    sigma_x, sigma_y = self.get_sigma()
    epsilon = self.get_epsilon()
    for name, mesh in (
        ("epsilon", epsilon),
        ("sigma_x", sigma_x),
        ("sigma_y", sigma_y),
    ):
        if mesh.shape != self.grid.shape:
            raise ValueError(
                f"{name} has shape {mesh.shape}; expected {self.grid.shape}."
            )
        if not numpy.isfinite(mesh.to_base_units().magnitude).all():
            raise ValueError(f"{name} contains non-finite values.")
    LOGGER.debug("Validated material meshes; configuring native solver")

    self._cpp_set_config(
        dt=self.grid.dt.to("second").magnitude,
        dx=self.grid.dx.to("meter").magnitude,
        dy=self.grid.dy.to("meter").magnitude,
        nx=self.grid.n_x,
        ny=self.grid.n_y,
        time_stamp=self.grid.time_stamp.to("second").magnitude,
    )

    self._cpp_set_geometry_mesh(
        epsilon=epsilon.to("farad/meter").magnitude,
        n2=(epsilon * 0)
        .to("farad/meter")
        .magnitude,  # Non-linear refractive index, if any
        gamma=(epsilon * 0)
        .to("farad/meter")
        .magnitude,  # Non-linear absorption, if any
        sigma_x=sigma_x.to("siemens/meter").magnitude,
        sigma_y=sigma_y.to("siemens/meter").magnitude,
        mu_0=Physics.mu_0.to("henry/meter").magnitude,
    )

    self._cpp_set_sources(sources=[s for s in self.sources])
    LOGGER.debug("Native solver configured; starting time integration")

    indexes = (
        numpy.concatenate([m.indexes for m in self.flux_monitors])
        if self.flux_monitors
        else numpy.empty((0, 3), dtype=numpy.int64)
    )
    monitor_data = numpy.empty((len(detector_steps), len(indexes), 2))
    self._cpp_set_monitors(monitor_data, indexes)
    shape = (n_recorded_steps, *self.grid.shape)
    if not store_fields:
        field_data = numpy.empty((0, *self.grid.shape))
    elif field_path is None:
        field_data = numpy.empty(shape)
    else:
        # Reserve exclusively: never truncate an existing simulation output.
        with field_path.open("xb"):
            pass
        field_data = numpy.lib.format.open_memmap(
            field_path, mode="w+", dtype=numpy.float64, shape=shape
        )

    self._cpp_run(
        Ez_time=field_data,
        record_every=field_every,
        detector_every=detector_every,
        detector_data=detector_data,
        detector_indexes=detector_indexes,
    )
    LOGGER.debug("Native time integration completed")

    self.Ez_t = field_data if store_fields else None
    self.recorded_time_stamp = self.grid.time_stamp[recorded_steps]
    detector_times = self.grid.time_stamp[detector_steps]
    flux = []
    offset = 0
    for monitor in self.flux_monitors:
        end = offset + len(monitor.indexes)
        flux.append(
            FluxRecord(
                monitor_data[:, offset:end],
                detector_times.copy() - self.grid.dt / 2,
                monitor.indexes.copy(),
                monitor.spacing,
                monitor.normal,
            )
        )
        offset = end
    if field_path is not None:
        field_data.flush()
        with Path(str(field_path) + ".metadata.npz").open("xb") as metadata:
            numpy.savez(
                metadata,
                time_seconds=self.recorded_time_stamp.to("second").magnitude,
                x_meters=self.grid.x_stamp.to("meter").magnitude,
                y_meters=self.grid.y_stamp.to("meter").magnitude,
            )
    self.result = SimulationResult.from_experiment(
        self,
        detector_data,
        detector_time_stamp=detector_times,
        flux=tuple(flux),
        field_path=field_path,
    )
    for detector, data in zip(self.detectors, detector_data.T):
        detector.update_data(data, time_stamp=detector_times)
    return self.result
