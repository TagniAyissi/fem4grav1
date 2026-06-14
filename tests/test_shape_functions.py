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
    def test_partition_of_unity(self):
        sizes = [(75, 100), (74, 101), (74, 100), (75, 101)]
        for irow, icol in sizes:
            with self.subTest(irow=irow, icol=icol):
                n_shape = shape_functions(irow, icol)
                self.assertTrue(np.allclose(np.sum(n_shape, axis=0), 1.0))

    def test_output_shape(self):
        n_shape = shape_functions(30, 40)
        self.assertEqual(n_shape.shape, (8, 30, 40))

if __name__ == "__main__":
    unittest.main()