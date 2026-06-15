#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import tempfile
import unittest
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fem4grav import run_fem 
from fem4grav.fem4grav import (
    load_xyz,
    regular_grid,
    save_table,
    separate_grid,
)

def write_sample_file(path: Path) -> None:
    """Generates a synthetic gravity survey dataset and writes it to disk. We use random uniform coordinates to simulate scattered field stations, 
    and a simple linear trend to simulate the measured gravity anomalies"""
    rng = np.random.default_rng(123)
    x = rng.uniform(13.8, 14.8, 40) #simulated Longitude
    y = rng.uniform(40.7, 41.0, 40) #simulated Latitude
    z = 5.0 + 0.1 * x - 0.05 * y #simulated gravity field
    np.savetxt(path, np.column_stack([x, y, z]), fmt="%.6f")

class TestSeparateGrid(unittest.TestCase):
    """Validates the core physical and mathematical assumptions of the regional/residual separation algorithm"""
    def test_constant_field_zero_residual(self):
        """If the observed gravity field is completely uniform (flat), there are no local mass anomalies. The algorithm must return 
        a residual field of exactly zero everywhere"""
        x_axis = np.linspace(0.0, 50.0, 51)
        y_axis = np.linspace(0.0, 30.0, 31)
        observed = np.full((31, 51), 7.5)

        result = separate_grid(observed, x_axis, y_axis)
        self.assertTrue(np.allclose(result.res_grid, 0.0, atol=1e-12))

    def test_output_shapes(self):
        """Ensure the separation process strictly preserves the spatial dimensions of the grid"""
        irow, icol = 20, 25
        x_axis = np.linspace(0.0, 10.0, icol)
        y_axis = np.linspace(0.0, 8.0, irow)
        observed = np.random.default_rng(0).uniform(-10, 10, (irow, icol))

        result = separate_grid(observed, x_axis, y_axis)
        self.assertEqual(result.obs_grid.shape, (irow, icol))
        self.assertEqual(result.reg_grid.shape, (irow, icol))
        self.assertEqual(result.res_grid.shape, (irow, icol))

    def test_observed_is_regional_plus_residual(self):
        """Tests the fundamental superposition principle of potential fields: The sum of the regional trend and the local residual must exactly 
        reconstruct the original observed gravity data"""
        x_axis = np.linspace(0.0, 100.0, 50)
        y_axis = np.linspace(0.0, 80.0, 40)
        observed = np.random.default_rng(42).normal(0, 10, (40, 50))

        result = separate_grid(observed, x_axis, y_axis)
        self.assertTrue(
            np.allclose(
                result.reg_grid + result.res_grid,
                result.obs_grid,
                atol=1e-12,
            )
        )

class TestFilesAndPipeline(unittest.TestCase):
    """Integration tests covering the entire end-to-end workflow: I/O operations, unstructured data gridding, and the main FEM execution"""
    def test_load_xyz(self):
        """Verify that we can correctly parse standard 3-column XYZ ASCII files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            fpath = Path(tmpdir) / "test.txt"
            write_sample_file(fpath)
            x, _y, z = load_xyz(fpath)

        self.assertEqual(x.shape, (40,))
        self.assertTrue(np.isfinite(z).all())

    def test_regular_grid_shape(self):
        """Gravity data often comes as unstructured point clouds from field surveys. This test ensures our interpolation logic safely projects these scattered 
        points onto a regular computational mesh without generating NaN values"""
        rng = np.random.default_rng(7)
        x = rng.uniform(13.8, 14.8, 60)
        y = rng.uniform(40.7, 41.0, 60)
        z = np.sin(x * 5) + np.cos(y * 5)

        x_axis, y_axis, grid = regular_grid(x, y, z, irow=20, icol=30)
        self.assertEqual(grid.shape, (20, 30))
        self.assertEqual(x_axis.shape, (30,))
        self.assertEqual(y_axis.shape, (20,))
        self.assertFalse(np.isnan(grid).any())

    def test_run_fem_pipeline(self):
        """Full end-to-end integration test. We feed a raw text file into the main wrapper function and ensure the entire FEM separation pipeline 
        executes and returns a valid data structure"""
        with tempfile.TemporaryDirectory() as tmpdir:
            fpath = Path(tmpdir) / "test.txt"
            write_sample_file(fpath)
            result = run_fem(str(fpath), irow=12, icol=15)

        self.assertEqual(result.obs_grid.shape, (12, 15))
        self.assertEqual(result.reg_nodes.shape, (8,))
        self.assertTrue(np.isfinite(result.res_grid).all())

    def test_save_table_header_and_rows(self):
        """Ensure the resulting separated grids are correctly flattened and exported back into an XYZ-style format for visualization software"""
        x_axis = np.linspace(0.0, 2.0, 3)
        y_axis = np.linspace(0.0, 1.0, 2)
        observed = np.ones((2, 3))
        result = separate_grid(observed, x_axis, y_axis)

        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "result.txt"
            save_table(result, output)
            lines = output.read_text(encoding="utf-8").splitlines()

        #the exported table should contain headers and the exact number of nodes
        self.assertEqual(lines[0], "x y observed regional residual")
        self.assertEqual(len(lines), 1 + observed.size)

if __name__ == "__main__":
    unittest.main()