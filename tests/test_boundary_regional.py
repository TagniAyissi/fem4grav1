#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import unittest
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fem4grav.fem4grav import (
    compute_regional,
    extract_nodes,
    separate_grid,
)

def linear_field(irow, icol):
    """Generate a synthetic gravity field with a perfect linear gradient. In gravity data processing, a simple plane (linear trend) is the most basic 
    representation of a regional field. We use this synthetic dataset as a baseline to ensure our separation algorithms behave perfectly when no local anomalies exist"""
    x_axis = np.linspace(0.0, 10.0, icol)
    y_axis = np.linspace(0.0, 6.0, irow)
    x_grid, y_grid = np.meshgrid(x_axis, y_axis)
    observed = 10.0 + 2.0 * x_grid + 3.0 * y_grid
    return x_axis, y_axis, observed

class TestBoundaryAndRegional(unittest.TestCase):
    """Unit tests for the regional/residual gravity separation pipeline. Validates boundary node extraction and the interpolation of the regional trend"""
    def test_linear_field_nodes(self):
        """Verify that the algorithm correctly identifies and extracts the boundary nodes from the observed gravity grid. We test against both odd and even grid dimensions 
        to ensure there are no off-by-one errors along the mesh edges"""

        #hardcoded expected values at the specific boundary nodes for our synthetic field
        expected = np.array([10, 20, 30, 39, 48, 38, 28, 19], dtype=float)

        for irow, icol in [(75, 100), (74, 101)]:
            with self.subTest(irow=irow, icol=icol):
                x_axis, y_axis, observed = linear_field(irow, icol)
                nodes = extract_nodes(observed, x_axis, y_axis) #check if the extracted boundary values match our theoretical expectations
                self.assertTrue(np.allclose(nodes, expected))

    def test_regional_reproduces_linear_field(self):
        """If we feed a perfectly linear field into our regional interpolation, the computed regional field should exactly match the input. This proves that 
        our FEM shape functions don't introduce any artificial curvature or distortion"""
        for irow, icol in [(75, 100), (74, 101)]:
            with self.subTest(irow=irow, icol=icol):
                x_axis, y_axis, observed = linear_field(irow, icol)
                nodes = extract_nodes(observed, x_axis, y_axis)
                regional = compute_regional(nodes, irow, icol)
                #the computed regional surface must be identical to the observed plane
                self.assertTrue(np.allclose(regional, observed, atol=1e-12))

    def test_zero_residual_linear_field(self):
        """The ultimate sanity check for anomaly separation: if the input data consists solely of a regional trend (our linear field), the resulting residual (local anomaly) 
        must be perfectly flat and equal to zero"""
        x_axis, y_axis, observed = linear_field(75, 100)
        result = separate_grid(observed, x_axis, y_axis)
        #the residual grid should essentially be a matrix of zeros
        self.assertTrue(np.allclose(result.res_grid, 0.0, atol=1e-12))

if __name__ == "__main__":
    unittest.main()