#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import unittest
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fem4grav.fem4grav import shape_functions 

class TestShapeFunctions(unittest.TestCase):
    """Unit tests for the Finite Element Method (FEM) shape functions"""

    def test_partition_of_unity(self):
        """Verify the partition of unity property. In FEM, the sum of all shape functions evaluated at any point in the domain 
        must exactly equal 1.0 to ensure rigid body modes are represented correctly"""
        #test across a few different grid dimensions (combinations of even/odd sizes) to ensure the function handles grid boundaries stably
        sizes = [(75, 100), (74, 101), (74, 100), (75, 101)]
        
        for irow, icol in sizes:
            with self.subTest(irow=irow, icol=icol):
                n_shape = shape_functions(irow, icol)
                #sum the shape functions along the node axis (axis=0) and check if the result is approximately 1.0 everywhere on the grid
                self.assertTrue(np.allclose(np.sum(n_shape, axis=0), 1.0))

    def test_output_shape(self):
        """Ensure the output array has the correct spatial dimensions and node count"""
        n_shape = shape_functions(30, 40)
        # We expect 8 shape functions (typically corresponding to an 8-node element) evaluated over the requested 30x40 grid
        self.assertEqual(n_shape.shape, (8, 30, 40))

if __name__ == "__main__":
    unittest.main()