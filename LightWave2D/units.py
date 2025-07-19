import pint

ureg = pint.UnitRegistry()
Quantity = ureg.Quantity


def to_meters(value) -> float:
    """Convert a value to meters if it's a pint Quantity or str."""
    if isinstance(value, pint.Quantity):
        return value.to(ureg.meter).magnitude
    if isinstance(value, str):
        return ureg.Quantity(value).to(ureg.meter).magnitude
    return float(value)
