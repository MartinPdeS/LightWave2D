"""Utility helpers for handling units with :mod:`pint`.

This module exposes Pint's :class:`~pint.Unit` objects so that units can
be used directly in expressions::

    from LightWave2D.units import nanometer
    diameter = 50 * nanometer

It also provides small helpers that generate quantities when called with a
value so that the previous ``units.meters(1)`` style still works.
"""

from __future__ import annotations

import pint


ureg = pint.UnitRegistry()
Quantity = ureg.Quantity

# expose common units as constants
meter = ureg.meter
micrometer = ureg.micrometer
nanometer = ureg.nanometer
millimeter = ureg.millimeter
centimeter = ureg.centimeter
second = ureg.second
femtosecond = ureg.femtosecond


def to_meters(value) -> float:
    """Return ``value`` converted to meters.

    Parameters
    ----------
    value:
        Either a numeric type, a string with units or a :class:`pint.Quantity`.

    Returns
    -------
    float
        ``value`` expressed in meters.
    """
    if isinstance(value, pint.Quantity):
        return value.to(ureg.meter).magnitude
    if isinstance(value, str):
        return ureg.Quantity(value).to(ureg.meter).magnitude
    return float(value)


def meters(value: float | int) -> Quantity:
    """Create a quantity expressed in meters."""

    return value * meter


def micrometers(value: float | int) -> Quantity:
    """Create a quantity expressed in micrometers."""

    return value * micrometer


def nanometers(value: float | int) -> Quantity:
    """Create a quantity expressed in nanometers."""

    return value * nanometer


def millimeters(value: float | int) -> Quantity:
    """Create a quantity expressed in millimeters."""

    return value * millimeter


def centimeters(value: float | int) -> Quantity:
    """Create a quantity expressed in centimeters."""

    return value * centimeter


def seconds(value: float | int) -> Quantity:
    """Create a quantity expressed in seconds."""

    return value * second


def femtoseconds(value: float | int) -> Quantity:
    """Create a quantity expressed in femtoseconds."""

    return value * femtosecond
