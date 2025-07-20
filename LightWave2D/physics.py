#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy
from dataclasses import dataclass
from LightWave2D import units


@dataclass(frozen=True)
class Physics():
    c: float = 3e8 * units.meter / units.second
    """ Speed of light in vacuum, m/s """
    epsilon_0: float = 8.854e-12 * units.farad / units.meter
    """ Permittivity of free space """
    mu_0: float = 4 * numpy.pi * 1e-7 * units.henry / units.meter
    """ Permeability of free space """
