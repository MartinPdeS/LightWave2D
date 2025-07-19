from typing import Optional

import pint
ureg = pint.UnitRegistry()

pint.set_application_registry(ureg)

# Define a list of base units to scale
BASE_UNITS = [
    'farad', 'henry', 'meter', 'second'
]

# Define prefixes for scaling units
SCALES = ['nano', 'micro', 'milli', '', 'kilo', 'mega', 'giga', 'tera']


def initialize_registry(ureg: Optional[object] = None):
    """
    Initialize and set up a unit registry. This function also leaks
    the units into the global namespace for easy access throughout
    the module.

    Parameters
    ----------
    ureg: Optional[pint.UnitRegistry]
        A UnitRegistry object to use. If None, the default PintType.ureg will be used.
    """

    # Leak scaled units into the global namespace
    for unit in BASE_UNITS:
        for scale in SCALES:
            scaled_unit_name = scale + unit
            globals()[scaled_unit_name] = getattr(ureg, scaled_unit_name)

    # Leak commonly used specific units into the global namespace
    common_units = {
        'farad': ureg.farad,
        'henry': ureg.henry,
        'coulomb': ureg.coulomb,
        'power': ureg.watt.dimensionality,
        'RIU': ureg.refractive_index_unit,
        'refractive_index_unit': ureg.refractive_index_unit,
        'distance': ureg.meter.dimensionality,
        'time': ureg.second.dimensionality,
        'Quantity': ureg.Quantity
    }

    # Leak the common units into the global namespace
    globals().update(common_units)

    globals()['ureg'] = ureg


initialize_registry(ureg)