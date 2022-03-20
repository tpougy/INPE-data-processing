import argparse

import os
import sys

# Create the parser
MRR_parser = argparse.ArgumentParser(
    description="Processes MRR data files to netCDF files"
)

# Add the arguments
MRR_parser.add_argument("-v", "--version", action="version", version="%(prog)s 0.1")

MRR_parser.add_argument(
    "-a",
    "--ave",
    action="store_true",
    default=None,
    help="Executes the script for .ave files and exit",
)
MRR_parser.add_argument(
    "-p",
    "--pro",
    action="store_true",
    default=None,
    help="Executes the script for .pro files and exit",
)
MRR_parser.add_argument(
    "-r",
    "--raw",
    action="store_true",
    default=None,
    help="Executes the script for .raw files and exit",
)

# Execute the parse_args() method
args = MRR_parser.parse_args()

# check if there is at least one action requested
if args.ave is None and args.raw is None and args.pro is None:
    MRR_parser.error("No action requested, see --help to further information")

import utils
from datetime import datetime, timedelta
from glob import glob
import pandas as pd
import numpy as np
from netCDF4 import Dataset
import time

all_var_list = np.loadtxt("./input/MRR/variables.dat", dtype=str)
all_var_list = list(all_var_list)

folder_selected = "./input/MRR/data"

if args.ave == True:
    selected = "ave"
    print("Processing .ave files")

    # reading all the files with the .ave extension
    PATH = folder_selected
    EXT = "*.ave"
    files = [
        file
        for path, subdir, files in os.walk(PATH)
        for file in glob(os.path.join(path, EXT))
    ]
    print("Total .ave files identified:", len(files))

    for file in files:

        print("Processing file:", file)

        [datetime_for_lines, data_per_var, widths_str] = utils.process_ave_files(
            selected, [file], all_var_list
        )

        utils.generate_netCDF(
            selected, datetime_for_lines, data_per_var, all_var_list, widths_str
        )

    print("All files processed")

if args.pro == True:
    selected = "pro"
    print("Processing .pro files")

    # reading all the files with the .pro extension
    PATH = folder_selected
    EXT = "*.pro"
    files = [
        file
        for path, subdir, files in os.walk(PATH)
        for file in glob(os.path.join(path, EXT))
    ]
    print("Total .pro files identified:", len(files))

    for file in files:

        print("Processing file:", file)

        [datetime_for_lines, data_per_var, widths_str] = utils.process_pro_files(
            selected, [file], all_var_list
        )

        utils.generate_netCDF(
            selected, datetime_for_lines, data_per_var, all_var_list, widths_str
        )

    print("All files processed")

if args.raw == True:
    selected = "raw"
    print("Processing .raw files")

    # reading all the files with the .raw extension
    PATH = folder_selected
    EXT = "*.raw"
    files = [
        file
        for path, subdir, files in os.walk(PATH)
        for file in glob(os.path.join(path, EXT))
    ]
    print("Total .raw files identified:", len(files))

    for file in files:

        print("Processing file:", file)

        [datetime_for_lines, data_per_var, widths_str] = utils.process_raw_files(
            selected, [file], all_var_list
        )

        utils.generate_netCDF(
            selected, datetime_for_lines, data_per_var, all_var_list, widths_str
        )

    print("All files processed")
