#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import annotations
from time import time
import argparse
import sys
from .__version__ import __version__
from .fem4grav import run_fem, save_grid, save_table, summary

def build_parser() -> argparse.ArgumentParser:
    """Constructs and returns the argument parser for the command-line interfac"""
    parser = argparse.ArgumentParser(
        prog="fem4grav",
        description="regional/residual separation of gravity anomalies with FEM",
    )
    #the input data file (made optional here to allow --version to run without a file)
    parser.add_argument("file", nargs="?", help="Input file with X Y anomaly columns")
    parser.add_argument("--version", "-v", action="store_true", help="Show version and exit") #version flag
    #grid dimension parameters
    parser.add_argument("--irow", type=int, default=75, help="Number of grid rows")
    parser.add_argument("--icol", type=int, default=101, help="Number of grid columns")
    #input file parsing options
    parser.add_argument("--skiprows", type=int, default=0, help="Header lines to skip")
    parser.add_argument("--delimiter", default=None, help="Column separator, for example ','")
    #spatial interpolation method selection
    parser.add_argument(
        "--method",
        choices=["nearest", "linear", "cubic"],
        default="cubic",
        help="Interpolation method used by scipy.griddata",
    )
    #data export options (NumPy arrays or standard text tables)
    parser.add_argument("--output", help="Save NumPy grids to this .npz file")
    parser.add_argument("--table", help="Save x y observed regional residual table")
    #visualization options
    parser.add_argument("--save-plot", dest="save_plot", metavar="FILE", help="Save the map figure")
    parser.add_argument("--no-plot", action="store_true", help="Do not open an interactive plot")
    return parser

def main(argv: list[str] | None = None) -> int:
    """Main execution pipeline for the CLI.
    Parses arguments, runs the FEM separation, and handles data/plot outputs"""

    #initialize the parser and read terminal inputs
    parser = build_parser()
    args = parser.parse_args(argv)
    #handle the --version flag: print the version and exit successfully
    if args.version:
        print(f"fem4grav v{__version__}")
        return 0
    #ensure a data file is provided if the version flag wasn't called
    if args.file is None:
        parser.error("The data file is required")
    #display execution parameters to the user
    print(f"fem4grav v{__version__}")
    print(f"File   : {args.file}")
    print(f"Grid   : {args.irow} x {args.icol}")
    print(f"Method : {args.method}")
    print()

    start = time()  #start tracking execution time
    
    try:
        #launch the core numerical modeling pipeline
        result = run_fem(
            args.file,
            irow=args.irow,
            icol=args.icol,
            skiprows=args.skiprows,
            method=args.method,
            delimiter=args.delimiter,
        )
    except Exception as exc:
        #catch and display any errors
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    #output the statistical and node summary to the terminal
    summary(result)
    print()
    print(f"Done in {time() - start:.2f} s")
    #handle the export of NumPy grid objects
    if args.output:
        save_grid(result, args.output)
        print(f"Saved npz   : {args.output}")
    #handle the export of the XYZ text table
    if args.table:
        save_table(result, args.table)
        print(f"Saved table : {args.table}")
    #handle spatial visualization (interactive display or saving to disk)
    if args.save_plot or not args.no_plot:
        from .plotting import plot_result #import plotting module only when needed to save memory and startup time
        plot_result(result, save_path=args.save_plot)
        if args.save_plot:
            print(f"Saved plot  : {args.save_plot}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())