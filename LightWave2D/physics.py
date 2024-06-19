#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy
from dataclasses import dataclass


@dataclass(frozen=True)
class Physics():
    c: float = 3e8
    """ Speed of light in vacuum, m/s """
    epsilon_0: float = 8.854e-12
    """ Permittivity of free space """
    mu_0: float = 4 * numpy.pi * 1e-7
    """ Permeability of free space """

# -
