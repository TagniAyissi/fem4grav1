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
    x_axis = np.linspace(0.0, 10.0, icol)
    y_axis = np.linspace(0.0, 6.0, irow)
    x_grid, y_grid = np.meshgrid(x_axis, y_axis)
    observed = 10.0 + 2.0 * x_grid + 3.0 * y_grid
    return x_axis, y_axis, observed

class TestBoundaryAndRegional(unittest.TestCase):
    def test_linear_field_nodes(self):
        expected = np.array([10, 20, 30, 39, 48, 38, 28, 19], dtype=float)

        for irow, icol in [(75, 100), (74, 101)]:
            with self.subTest(irow=irow, icol=icol):
                x_axis, y_axis, observed = linear_field(irow, icol)
                nodes = extract_nodes(observed, x_axis, y_axis)
                self.assertTrue(np.allclose(nodes, expected))

    def test_regional_reproduces_linear_field(self):
        for irow, icol in [(75, 100), (74, 101)]:
            with self.subTest(irow=irow, icol=icol):
                x_axis, y_axis, observed = linear_field(irow, icol)
                nodes = extract_nodes(observed, x_axis, y_axis)
                regional = compute_regional(nodes, irow, icol)
                self.assertTrue(np.allclose(regional, observed, atol=1e-12))

    def test_zero_residual_linear_field(self):
        x_axis, y_axis, observed = linear_field(75, 100)
        result = separate_grid(observed, x_axis, y_axis)
        self.assertTrue(np.allclose(result.res_grid, 0.0, atol=1e-12))

if __name__ == "__main__":
    unittest.main()