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
    """Unit tests for the middle_value function. This function is crucial for extracting or interpolating the reference value 
    at the exact center of our 1D axes (useful for setting boundary conditions or reference points in gravity models)"""
    def test_odd_grid(self):
        """When the grid has an odd number of nodes, the geometric center falls exactly on an existing node. We need to verify that the function 
        fetches the exact value without introducing interpolation errors"""
        axis = np.linspace(0.0, 10.0, 5) #center is exactly at index 2 (axis=5.0)
        values = 2.0 * axis + 1.0
        self.assertAlmostEqual(middle_value(axis, values), 11.0)

    def test_even_grid(self):
        """For an even number of nodes, the true center lies in the gap between two nodes. This test ensures our interpolation correctly averages or calculates 
        the midpoint value based on the surrounding mesh points"""
        axis = np.linspace(0.0, 10.0, 6)
        values = 2.0 * axis + 1.0
        self.assertAlmostEqual(middle_value(axis, values), 11.0)

    def test_reversed_axis(self):
        """In geophysics, it's very common to have inverted axes. We need to ensure the interpolation 
        logic remains robust and doesn't break if the coordinate array is sorted backwards"""
        axis = np.linspace(0.0, 10.0, 6)
        values = 2.0 * axis + 1.0
        self.assertAlmostEqual(middle_value(axis[::-1], values[::-1]), 11.0)

    def test_duplicated_coordinates(self):
        """Overlapping nodes (zero distance between two points) are a common mesh generation bug that causes division by zero or infinite gradients during interpolation. 
        We want the function to fail loudly and catch this geometry error early"""
        with self.assertRaises(ValueError):
            middle_value(
                np.array([0.0, 1.0, 1.0]),
                np.array([0.0, 1.0, 2.0]),
            )

if __name__ == "__main__":
    unittest.main()