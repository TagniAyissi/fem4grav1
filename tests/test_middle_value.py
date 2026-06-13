#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fem4grav.fem4grav import middle_value 

class TestMiddleValue(unittest.TestCase):
    def test_odd_grid(self):
        axis = np.linspace(0.0, 10.0, 5)
        values = 2.0 * axis + 1.0
        self.assertAlmostEqual(middle_value(axis, values), 11.0)

    def test_even_grid(self):
        axis = np.linspace(0.0, 10.0, 6)
        values = 2.0 * axis + 1.0
        self.assertAlmostEqual(middle_value(axis, values), 11.0)

    def test_reversed_axis(self):
        axis = np.linspace(0.0, 10.0, 6)
        values = 2.0 * axis + 1.0
        self.assertAlmostEqual(middle_value(axis[::-1], values[::-1]), 11.0)

    def test_duplicated_coordinates(self):
        with self.assertRaises(ValueError):
            middle_value(
                np.array([0.0, 1.0, 1.0]),
                np.array([0.0, 1.0, 2.0]),
            )

if __name__ == "__main__":
    unittest.main()