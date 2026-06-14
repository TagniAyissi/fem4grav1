#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for the fem4grav package. This suite ensures that the validation rules, core math functions, 
and CLI commands work exactly as expected"""

import sys
import unittest
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from fem4grav import __version__  
from fem4grav.cli import main  
from fem4grav.fem4grav import (  
    compute_regional,
    extract_nodes,
    separate_grid,
    summary,
    validate_grid,
)

class TestValidation(unittest.TestCase):
    """Test suite for the input validation logic"""

    def test_invalid_grid_size_type(self):
        # the grid dimensions must be integers. passing a float (10.0) should raise a TypeError
        with self.assertRaises(TypeError):
            validate_grid(10.0, 10)

    def test_value_too_small(self):
        #a grid must be at least 2x2 to define boundary nodes. passing 1 row should raise a ValueError
        with self.assertRaises(ValueError):
            validate_grid(1, 10)

    def test_compute_regional_wrong_node_count(self):
        #the serendipity finite element explicitly requires exactly 8 boundary nodes. passing an array of 7 nodes must fail and raise a ValueError
        with self.assertRaises(ValueError):
            compute_regional(np.ones(7), 3, 3)

    def test_1d_grid(self):
        #extract_nodes expects a 2D matrix (irow, icol). passing a 1D array will break the shape unpacking, so we expect a ValueError
        with self.assertRaises(ValueError):
            extract_nodes(np.ones(3), np.arange(3), np.arange(3))

class TestCli(unittest.TestCase):
    """Test suite for the Command Line Interface and output summaries"""

    def test_version(self):
        #ensure that calling the CLI with the --version flag exits cleanly with a success code (0)
        self.assertEqual(main(["--version"]), 0)

    def test_version_type(self):
        #verify that the version number is correctly formatted as a string
        self.assertIsInstance(__version__, str)

    def test_summary_no_error(self):
        #create dummy geographical axes and a random 2D gravity anomaly grid
        x_axis = np.linspace(13.8, 14.8, 11)
        y_axis = np.linspace(40.7, 41.4, 9)
        observed = np.random.default_rng(99).uniform(-20, 20, (9, 11))
        #run the FEM separation to generate a complete FemResult object
        result = separate_grid(observed, x_axis, y_axis)
        #call the summary function to ensure it formats and prints the data without crashing. if no exception is thrown, the test passes naturally
        summary(result)

if __name__ == "__main__":
    unittest.main()