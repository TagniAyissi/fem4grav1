##!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plotting helpers for the three FEM maps.
This module handles the spatial visualization of the gravity grids.
"""

from __future__ import annotations
import os
from os import PathLike
from .fem4grav import FemResult

TextPath = str | PathLike[str]

def _imshow(ax, grid, extent, cmap, symmetric=False):
    """Helper function to wrap matplotlib's imshow with standardized parameters.
    
    Parameters:
    ax        : matplotlib.axes.Axes
        The axes on which to draw the image.
    grid      : np.ndarray
        The 2D data array to plot.
    extent    : list
        Bounding box [xmin, xmax, ymin, ymax] for spatial coordinates.
    cmap      : str
        Colormap to use.
    symmetric : bool
        If True, forces the color scale to be symmetric around zero. 
        This is crucial for residual anomalies where positive and negative 
        values must be clearly distinguished around a 0 mGal baseline"""
    im_kw = {}
    if symmetric:
        #calculate the maximum absolute value to center the colormap on 0
        vmax = max(abs(float(grid.min())), abs(float(grid.max())))
        im_kw = {"vmin": -vmax, "vmax": vmax}

    #render the 2D grid
    return ax.imshow(
        grid,
        extent=extent,
        origin="lower",  #standard for geographic data (Y increases upwards)
        cmap=cmap,
        aspect="auto",
        interpolation="bilinear", #smooths out grid pixels for a natural look
        **im_kw,
    )

def plot_result(
    result: FemResult,
    save_path: TextPath | None = None,
    cmap: str = "coolwarm",
    title: str = "Campi Flegrei - Bouguer anomaly",
) -> None:
    """Generate and display (or save) the observed, regional, and residual maps.
    If a save_path is provided, this function will save individual maps 
    as well as a combined 3-panel figure"""
    #lazy import to speed up CLI execution if plotting is not requested
    import matplotlib.pyplot as plt
    #define the geographical boundaries for the plot axes
    extent = [
        result.x_axis.min(),
        result.x_axis.max(),
        result.y_axis.min(),
        result.y_axis.max(),
    ]
    #define the configuration for the three panels: (data_grid, title, symmetric_colormap_flag, filename)
    panels = [
        (result.obs_grid, "Bouguer anomaly", False, "bouguer.png"),
        (result.reg_grid, "Regional field", False, "regional.png"),
        (result.res_grid, "Residual anomaly", True, "residual.png"),
    ]

    #save Individual Maps
    #if a path is specified, we generate and save a separate high-res image for each grid
    if save_path is not None:
        out_dir = os.path.dirname(save_path) or "."
        os.makedirs(out_dir, exist_ok=True) # Ensure output directory exists
        for grid, label, symmetric, filename in panels:
            fig, ax = plt.subplots(figsize=(6, 5), constrained_layout=True)
            im = _imshow(ax, grid, extent, cmap, symmetric=symmetric)
            #map styling
            ax.set_title(label, fontsize=11)
            ax.set_xlabel("Longitude")
            ax.set_ylabel("Latitude")
            fig.colorbar(im, ax=ax, label="mGal")
            #export to disk
            path = os.path.join(out_dir, filename)
            fig.savefig(path, dpi=300, bbox_inches="tight")
            plt.close(fig) #free up memory
            print(f"  individual map: {path}")

    #reate combined 3-panel figure
    fig, axes = plt.subplots(1, 3, figsize=(18, 5), constrained_layout=True)
    for ax, (grid, label, symmetric, _filename) in zip(axes, panels):
    #we use '_filename' to indicate that while we must unpack 4 items from the tuple, 
    #this specific variable is intentionally ignored here
        im = _imshow(ax, grid, extent, cmap, symmetric=symmetric)
        #panel styling
        ax.set_title(label, fontsize=11)
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        #add a slightly shrunken colorbar for aesthetics
        cbar = fig.colorbar(im, ax=ax, label="mGal", shrink=0.9)
        cbar.ax.tick_params(labelsize=8)
    #add the main overarching title
    fig.suptitle(title, fontsize=13)

    #display or Export
    if save_path is None:
        plt.show()
    else:
        #save the combined figure to the specified path
        fig.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        print(f"  combined map: {save_path}")