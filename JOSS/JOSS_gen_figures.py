# ##################### IMPORTS ####################

import argparse
import pathlib
import numpy as np
import json
from datetime import datetime
from netCDF4 import Dataset
import os
import time

import utils

# ##################### ARGUMENTS ######################

# Create the parser
JOSS_parser = argparse.ArgumentParser(
    description="Generate figures for JOSS netCDF files"
)

# Add the arguments
JOSS_parser.add_argument("-v", "--version", action="version", version="%(prog)s 0.1")

JOSS_parser.add_argument(
    "-s",
    "--standard",
    action="store_true",
    default=None,
    help="Executes the script for all .nc files inside the data_figures input folder and exit",
)

JOSS_parser.add_argument(
    "-l",
    "--list",
    action="store_true",
    default=None,
    help="Executes the script for files listed in the files_figures.txt file specified ate input/JOSS folder and exit. The file.txt must have only the file name (without path) of the files in each line.",
)

JOSS_parser.add_argument(
    "-p",
    "--png",
    action="store_true",
    default=None,
    help="Generates only the .png files.",
)


# Execute the parse_args() method
args = JOSS_parser.parse_args()

# check if there is at least one action requested
if args.standard is None and args.list is None:
    JOSS_parser.error("No action requested, see --help to further information")

if args.standard is not None and args.list is not None:
    JOSS_parser.error("Invalid action requested, see --help to further information")

# ##################### SCRIPT #####################

# Folders and files path
path_cwd = pathlib.Path.cwd().joinpath("JOSS")

if path_cwd.name != "JOSS":
    print(
        "ERRO. Please make sure python current working directory is the /JOSS folder which contains this script"
    )
    print("ERRO. Current working directory is:", path_cwd)
    quit()

path_input = path_cwd.joinpath("input", "JOSS")
path_input_data_figures = path_input.joinpath("data_figures")
path_input_support = path_input.joinpath("support")

path_output = path_cwd.joinpath("output", "JOSS")
path_output_fig = path_output.joinpath("figures")

# reading auxiliar data
with open(path_input_support.joinpath("variables_info.json"), "r") as xfile:
    variables_info_file = xfile.read()
variables_info = json.loads(variables_info_file)
with open(path_input_support.joinpath("netCDF_info.json"), "r") as xfile:
    netCDF_info_file = xfile.read()
netCDF_info = json.loads(netCDF_info_file)

# reading all file names in folder or list
EXT = ".nc"
if args.standard:
    print("Executing script in standard mode")
    print("")
    files = [
        path_input_data_figures.joinpath(file)
        for file in os.listdir(path_input_data_figures)
        if file.endswith(EXT)
    ]
elif args.list:
    print("Executing script in list mode")
    print("")
    files = np.loadtxt(path_input.joinpath("files.txt"), dtype=str)
    if len(files.shape) == 0:
        files = files.reshape(1)
    files = [path_input_data.joinpath(file) for file in files]

if args.png:
    print("Executing script in png mode. Only PNG files are included in the output")

for file in files:
    print("Generating figures for file {}".format(file.name))
    output_folder = path_output_fig.joinpath(str(file.name)[:-3])
    pathlib.Path(output_folder).mkdir(parents=True, exist_ok=True)

    file_data = Dataset(file, "r")

    time_index_file_data = [
        datetime.utcfromtimestamp(x)
        for x in file_data["Time offset base_time"][:] + file_data["Base time"][:]
    ]

    fig_metadata = {"disdrometer": "RD-80", "site": "Atto-Campina"}

    list_variables_1D = ["rain_rate", "zdb", "liq_water"]

    for var in list_variables_1D:
        print("\tFigure for variable {}".format(var))
        utils.gen_fig_1D(
            file_data[netCDF_info["variables"][var]["name"]][:],
            time_index_file_data,
            netCDF_info["variables"][var]["name"],
            netCDF_info["variables"][var]["unit"],
            fig_metadata,
            output_folder,
            args.png,
        )

    if not args.png:
        print("\tFigure for variable {}".format("Rain Rate and NDropxDi"))
        utils.gen_fig_NDropxDi(
            time_index_file_data,
            file_data["Rain Rate"],
            variables_info["drop_class"],
            file_data["Number of raindrops"],
            fig_metadata,
            output_folder,
        )
