#!/usr/bin/python
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from os import PathLike

import numpy as np

TextPath = str | PathLike[str]

@dataclass
class FemResult:
    x_axis: np.ndarray
    y_axis: np.ndarray
    obs_grid: np.ndarray
    reg_grid: np.ndarray
    res_grid: np.ndarray
    reg_nodes: np.ndarray

def validate_grid(irow: int, icol: int):
    if not isinstance(irow, int) or not isinstance(icol, int):
        raise TypeError("irow and icol must be integers")
    if irow < 2 or icol < 2:
        raise ValueError("irow and icol must be >= 2")

def _validate_xyz(x, y, z):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    z = np.asarray(z, dtype=float)

    if x.ndim != 1 or y.ndim != 1 or z.ndim != 1:
        raise ValueError("x, y and z must be 1D arrays")
    if x.size != y.size or x.size != z.size:
        raise ValueError("x, y and z must have the same length")
    if x.size < 3:
        raise ValueError("at least 3 points are needed")
    if not (np.isfinite(x).all() and np.isfinite(y).all() and np.isfinite(z).all()):
        raise ValueError("x, y and z must contain only finite values")

    return x, y, z

def _sort_xy(axis, values):
    axis = np.asarray(axis, dtype=float)
    values = np.asarray(values, dtype=float)

    if axis.ndim != 1 or values.ndim != 1 or axis.size != values.size:
        raise ValueError("axis and values must be 1D arrays with the same length")
    if axis.size < 2:
        raise ValueError("axis must contain at least 2 values")
    if not (np.isfinite(axis).all() and np.isfinite(values).all()):
        raise ValueError("axis and values must contain only finite values")

    idx = np.argsort(axis)
    axis = axis[idx]
    values = values[idx]

    if np.any(np.diff(axis) <= 0.0):
        raise ValueError("axis coordinates must be unique")

    return axis, values

def load_xyz(file_name: TextPath, skiprows=0, delimiter=None):
    data = np.loadtxt(file_name, skiprows=skiprows, delimiter=delimiter)
    if data.ndim != 2 or data.shape[1] < 3:
        raise ValueError("file must contain at least three columns: x, y, anomaly")
    return _validate_xyz(data[:, 0], data[:, 1], data[:, 2])

def save_grid(result: FemResult, file_name: TextPath):
    np.savez(
        file_name,
        x_axis=result.x_axis,
        y_axis=result.y_axis,
        obs_grid=result.obs_grid,
        reg_grid=result.reg_grid,
        res_grid=result.res_grid,
        reg_nodes=result.reg_nodes,
    )

def save_table(result: FemResult, file_name: TextPath):
    x_grid, y_grid = np.meshgrid(result.x_axis, result.y_axis)
    table = np.column_stack(
        [
            x_grid.ravel(),
            y_grid.ravel(),
            result.obs_grid.ravel(),
            result.reg_grid.ravel(),
            result.res_grid.ravel(),
        ]
    )
    np.savetxt(file_name, table, header="x y observed regional residual", comments="", fmt="%.10g")

def regular_grid(x, y, z, irow: int, icol: int, method="cubic"):
    from scipy.interpolate import griddata

    validate_grid(irow, icol)
    if method not in {"nearest", "linear", "cubic"}:
        raise ValueError("method must be 'nearest', 'linear' or 'cubic'")

    x, y, z = _validate_xyz(x, y, z)

    x_axis = np.linspace(float(np.min(x)), float(np.max(x)), icol)
    y_axis = np.linspace(float(np.min(y)), float(np.max(y)), irow)
    x_grid, y_grid = np.meshgrid(x_axis, y_axis)

    obs_grid = griddata((x, y), z, (x_grid, y_grid), method=method)

    # cubic and linear interpolation sometimes leave empty cells on the border
    if np.isnan(obs_grid).any():
        nearest = griddata((x, y), z, (x_grid, y_grid), method="nearest")
        obs_grid = np.where(np.isnan(obs_grid), nearest, obs_grid)

    return x_axis, y_axis, obs_grid

def middle_value(axis, values):
    axis, values = _sort_xy(axis, values)
    middle_coord = 0.5 * (axis[0] + axis[-1])
    return float(np.interp(middle_coord, axis, values))

def extract_nodes(obs_grid, x_axis, y_axis):
    obs_grid = np.asarray(obs_grid, dtype=float)
    if obs_grid.ndim != 2:
        raise ValueError("obs_grid must be a 2D array")

    irow, icol = obs_grid.shape
    validate_grid(irow, icol)

    if len(x_axis) != icol or len(y_axis) != irow:
        raise ValueError("x_axis/y_axis do not match the grid size")
    if not np.isfinite(obs_grid).all():
        raise ValueError("obs_grid must contain only finite values")

    node_1 = obs_grid[0, 0]
    node_2 = middle_value(x_axis, obs_grid[0, :])
    node_3 = obs_grid[0, -1]
    node_4 = middle_value(y_axis, obs_grid[:, -1])
    node_5 = obs_grid[-1, -1]
    node_6 = middle_value(x_axis, obs_grid[-1, :])
    node_7 = obs_grid[-1, 0]
    node_8 = middle_value(y_axis, obs_grid[:, 0])

    return np.array([node_1, node_2, node_3, node_4, node_5, node_6, node_7, node_8])
