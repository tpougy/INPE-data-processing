# ##################### IMPORTS ####################

import argparse
import numpy as np
import pandas as pd
from datetime import datetime
import os
import pathlib
import json
import utils

# ##################### ARGUMENTS ######################

# Create the parser
JOSS_parser = argparse.ArgumentParser(
    description="Processes JOSS raw data files to netCDF files"
)

# Add the arguments
JOSS_parser.add_argument("-v", "--version", action="version", version="%(prog)s 0.1")

JOSS_parser.add_argument(
    "-d",
    "--date",
    action="store",
    default=None,
    help="Expect exporting date in format dd/mm/YYYY",
)
JOSS_parser.add_argument(
    "-s",
    "--standard",
    action="store_true",
    default=None,
    help="Executes the script for all .trf files inside the data input folder and exit",
)
JOSS_parser.add_argument(
    "-l",
    "--list",
    action="store_true",
    default=None,
    help="Executes the script for files listed in the files.txt file specified ate input/JOSS folder and exit. The file.txt must have only the file name (without path) of the files in each line.",
)

# Execute the parse_args() method
args = JOSS_parser.parse_args()

# if args.date is None:
if not args.date:
    export_date = args.date
else:
    try:
        export_date = datetime.strptime(args.date, "%d/%m/%Y")
    except:
        JOSS_parser.error("Bad date format, see --help to further information")

# check if there is at least one action requested
if args.standard is None and args.list is None:
    JOSS_parser.error("No action requested, see --help to further information")

if args.standard is not None and args.list is not None:
    JOSS_parser.error("Invalid action requested, see --help to further information")

# ##################### SCRIPT #####################

# Folders and files path
path_cwd = pathlib.Path.cwd()

print(path_cwd.name)

if path_cwd.name != "JOSS":
    print(
        "ERRO. Please make sure python current working directory is the /JOSS folder which contains this script"
    )
    print("ERRO. Current working directory is:", path_cwd)
    quit()

path_input = path_cwd.joinpath("input", "JOSS")
path_input_data = path_input.joinpath("data")
path_input_support = path_input.joinpath("support")

path_output = path_cwd.joinpath("output", "JOSS")
path_output_data = path_output.joinpath("netCDF")

# reading auxiliar data
with open(path_input_support.joinpath("variables_info.json"), "r") as xfile:
    variables_info_file = xfile.read()
variables_info = json.loads(variables_info_file)

with open(path_input_support.joinpath("netCDF_info.json"), "r") as xfile:
    netCDF_info_file = xfile.read()
netCDF_info = json.loads(netCDF_info_file)

columns = list(np.loadtxt(path_input_support.joinpath("variables.txt"), dtype=str))

# reading all file names in folder or list
EXT = ".trf"
if args.standard:
    print("Executing script in standard mode")
    print("")
    files = [
        path_input_data.joinpath(file)
        for file in os.listdir(path_input_data)
        if file.endswith(EXT)
    ]
elif args.list:
    print("Executing script in list mode")
    print("")
    files = np.loadtxt(path_input.joinpath("files.txt"), dtype=str)
    if len(files.shape) == 0:
        files = files.reshape(1)
    files = [path_input_data.joinpath(file) for file in files]

# data processing
while True:
    # # chama a funçao que le os dados
    (export_date, day_data, flag) = utils.process_files(
        files, columns, export_date, variables_info
    )

    if flag:
        break

    if day_data.shape[0] != 0:

        cdf_filename = (
            "att"
            + "impactdisd"
            + "cam."
            + "b0."
            + day_data.index[0].strftime("%Y%m%d.%H%M%S")
            + ".nc"
        )

        utils.generate_netCDF(
            cdf_filename,
            day_data,
            columns,
            variables_info,
            netCDF_info,
            path_input,
            path_output_data,
        )
        print("")

    if args.date:
        break

# end of data processing
print("All data have been processed.")
quit()
