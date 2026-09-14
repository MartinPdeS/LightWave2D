"""Stored outputs of one simulation, independent of subsequent runs."""

from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any
import numpy as np


@dataclass(frozen=True)
class SimulationResult:
    """One run's field history, timestamps, and detector samples.

    ``detector_data`` has shape (detector samples, detectors), in insertion order,
    with ``detector_time_stamp`` timestamps. ``recorded_time_stamp`` belongs to
    field frames and may have a different cadence. ``flux`` holds FluxRecords.
    ``Ez_t`` is a NumPy array or disk-backed memmap, or None for detector-only runs. Arrays are owned by this run and
    remain available when the experiment runs again. Geometry overlays retain
    references to the configured objects; array contents remain user-editable.
    """

    Ez_t: np.ndarray | None
    recorded_time_stamp: Any
    detector_data: np.ndarray
    grid: Any
    components: tuple = ()
    sources: tuple = ()
    detectors: tuple = ()

    detector_time_stamp: Any = None
    flux: tuple = ()
    field_path: Any = None

    def detector_spectrum(self, detector=0, *, window="hann"):
        """Return frequency bins in Hz and complex point-detector amplitudes."""
        from LightWave2D.monitors import FieldSpectrum, fourier

        frequency, amplitude = fourier(
            self.detector_data[:, detector], self.detector_time_stamp, window
        )
        return FieldSpectrum(frequency, amplitude)

    @classmethod
    def from_experiment(
        cls,
        experiment,
        detector_data,
        *,
        detector_time_stamp=None,
        flux=(),
        field_path=None,
    ):
        grid = SimpleNamespace(
            x_stamp=experiment.grid.x_stamp.copy(),
            y_stamp=experiment.grid.y_stamp.copy(),
        )
        return cls(
            experiment.Ez_t,
            experiment.recorded_time_stamp.copy(),
            detector_data,
            grid,
            tuple(experiment.components),
            tuple(experiment.sources),
            tuple(experiment.detectors),
            (
                detector_time_stamp
                if detector_time_stamp is not None
                else experiment.recorded_time_stamp.copy()
            ),
            flux,
            field_path,
        )

    @classmethod
    def load_fields(cls, path):
        """Reopen disk-backed fields and coordinate metadata read-only.

        Detector signals and geometry overlays are not stored in this format.
        Missing metadata indicates an incomplete recording.
        """
        from pathlib import Path
        from TypedUnit import ureg

        path = Path(path).resolve()
        with np.load(str(path) + ".metadata.npz", allow_pickle=False) as metadata:
            times = metadata["time_seconds"] * ureg.second
            grid = SimpleNamespace(
                x_stamp=metadata["x_meters"] * ureg.meter,
                y_stamp=metadata["y_meters"] * ureg.meter,
            )
        fields = np.load(path, mmap_mode="r", allow_pickle=False)
        if fields.shape != (len(times), len(grid.x_stamp), len(grid.y_stamp)):
            raise ValueError("Field data and metadata shapes do not match.")
        return cls(
            fields,
            times,
            np.empty((len(times), 0)),
            grid,
            detector_time_stamp=times,
            field_path=path,
        )

    def _require_field_history(self):
        if self.Ez_t is None:
            raise RuntimeError(
                "No field history was stored. Re-run with store_fields=True to plot or render fields."
            )
        return self.Ez_t

    def plot_frame(self, *args, **kwargs):
        """Plot a recorded frame; accepts visualization.plot_frame arguments."""
        from LightWave2D.visualization import plot_frame

        return plot_frame(self, *args, **kwargs)

    def render_propagation(self, *args, **kwargs):
        """Animate recorded frames; accepts visualization.render_propagation arguments."""
        from LightWave2D.visualization import render_propagation

        return render_propagation(self, *args, **kwargs)
