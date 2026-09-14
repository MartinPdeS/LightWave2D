"""Axis-aligned line monitors and Fourier analysis of recorded fields."""

from dataclasses import dataclass
import numpy as np


def fourier(data, time_stamp, window="hann"):
    """Return Hz bins and one-sided complex amplitudes (coherent-gain scaling)."""
    times = np.asarray(time_stamp.to("second").magnitude)
    if data.shape[0] != len(times):
        raise ValueError("Samples and timestamps must have matching lengths.")
    if len(times) < 2:
        raise ValueError("Spectra require at least two samples.")
    dt = np.diff(times)
    if dt[0] <= 0 or not np.allclose(dt, dt[0], rtol=1e-8, atol=0):
        raise ValueError("Spectra require uniformly spaced, increasing timestamps.")
    if window not in ("hann", "boxcar"):
        raise ValueError("window must be 'hann' or 'boxcar'.")
    weights = np.hanning(len(times)) if window == "hann" else np.ones(len(times))
    if weights.sum() == 0:
        raise ValueError("The Hann window requires at least three samples.")
    shape = (len(times),) + (1,) * (data.ndim - 1)
    amplitude = np.fft.rfft(data * weights.reshape(shape), axis=0) * (2 / weights.sum())
    amplitude[0] *= 0.5
    if len(times) % 2 == 0:
        amplitude[-1] *= 0.5
    return np.fft.rfftfreq(len(times), dt[0]), amplitude


@dataclass(frozen=True)
class FieldSpectrum:
    """Frequency in Hz and complex electric-field amplitude in solver units."""

    frequency: np.ndarray
    amplitude: np.ndarray


@dataclass(frozen=True)
class FluxSpectrum:
    """Signed line-integrated spectral power per unit out-of-plane length.

    Values use W/m when source electric amplitudes are interpreted as V/m.
    These are coherent-gain-normalized Fourier-bin powers, not a power spectral
    density. Use identical durations and windows for pulse-run normalization.
    """

    frequency: np.ndarray
    power: np.ndarray

    def normalized(self, reference, *, cutoff=1e-6):
        """Divide by reference power; weak incident bins become NaN.

        Opposite monitor normals give opposite signs. Negate a reflected/incident
        ratio when both monitors point along incident propagation.
        """
        if not np.array_equal(self.frequency, reference.frequency):
            raise ValueError("Reference frequency bins must match.")
        if not 0 <= cutoff < 1:
            raise ValueError("cutoff must be in [0, 1).")
        denominator = np.abs(reference.power)
        valid = (denominator > cutoff * denominator.max()) & (denominator > 0)
        return np.divide(
            self.power,
            reference.power,
            out=np.full_like(self.power, np.nan),
            where=valid,
        )


class FluxMonitor:
    """A line of Ez and spatially/temporally centered tangential H samples.

    Endpoints must define a horizontal or vertical line inside the grid.
    normal is +1 or -1 along x for vertical lines and y for horizontal lines.
    """

    def __init__(self, *, grid, position_0, position_1, normal=1):
        self.p0 = grid.get_coordinate(x=position_0[0], y=position_0[1])
        self.p1 = grid.get_coordinate(x=position_1[0], y=position_1[1])
        x0, y0 = self.p0.x_index, self.p0.y_index
        x1, y1 = self.p1.x_index, self.p1.y_index
        if normal not in (-1, 1):
            raise ValueError("normal must be +1 or -1.")
        if (x0 == x1) == (y0 == y1):
            raise ValueError("Flux monitor must be a nonzero axis-aligned line.")
        self.axis = 0 if x0 == x1 else 1
        self.normal = normal
        self.indexes = np.array(
            (
                [(x0, y, 0) for y in range(min(y0, y1), max(y0, y1) + 1)]
                if self.axis == 0
                else [(x, y0, 1) for x in range(min(x0, x1), max(x0, x1) + 1)]
            ),
            dtype=np.int64,
        )
        if (
            np.any(self.indexes[:, :2] < 1)
            or np.any(self.indexes[:, 0] >= grid.n_x - 1)
            or np.any(self.indexes[:, 1] >= grid.n_y - 1)
        ):
            raise ValueError(
                "Flux monitors must lie at least one cell inside grid boundaries."
            )
        self.spacing = float(
            (grid.dy if self.axis == 0 else grid.dx).to("meter").magnitude
        )

    def add_to_ax(self, ax):
        return ax.plot(
            [self.p0.x.to("meter").magnitude, self.p1.x.to("meter").magnitude],
            [self.p0.y.to("meter").magnitude, self.p1.y.to("meter").magnitude],
            color="green",
        )[0]


@dataclass(frozen=True)
class FluxRecord:
    """One monitor's centered E/H samples, timestamps and integration weights."""

    data: np.ndarray
    time_stamp: object
    indexes: np.ndarray
    spacing: float
    normal: int

    def spectrum(self, *, window="hann", subtract=None):
        data = self.data
        if subtract is not None:
            if (
                data.shape != subtract.data.shape
                or not np.array_equal(self.indexes, subtract.indexes)
                or self.spacing != subtract.spacing
                or self.normal != subtract.normal
                or not np.array_equal(
                    self.time_stamp.to("second").magnitude,
                    subtract.time_stamp.to("second").magnitude,
                )
            ):
                raise ValueError(
                    "Subtracted reference must have matching geometry and sampling."
                )
            # Subtract fields before forming power to isolate reflected waves.
            data = data - subtract.data
        frequency, amplitude = fourier(data, self.time_stamp, window)
        density = 0.5 * np.real(amplitude[:, :, 0] * amplitude[:, :, 1].conj())
        density[0] *= 2
        if len(data) % 2 == 0:
            density[-1] *= 2
        power = np.trapezoid(density, dx=self.spacing, axis=1) * self.normal
        return FluxSpectrum(frequency, power)
