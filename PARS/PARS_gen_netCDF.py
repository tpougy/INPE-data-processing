import argparse
import pathlib
import json
import os

from datetime import datetime

import numpy as np

import utils

# ##################### ARGUMENTS ######################

# Create the parser
PARS_parser = argparse.ArgumentParser(
    description="Processes PARS raw data files to netCDF files"
)

# Add the arguments
PARS_parser.add_argument("-v", "--version", action="version", version="%(prog)s 0.1")

PARS_parser.add_argument(
    "-d",
    "--date",
    action="store",
    default=None,
    help="Expect exporting date in format dd/mm/YYYY",
)
PARS_parser.add_argument(
    "-s",
    "--standard",
    action="store_true",
    default=None,
    help="Executes the script for all .trf files inside the data input folder and exit",
)
PARS_parser.add_argument(
    "-l",
    "--list",
    action="store_true",
    default=None,
    help="Executes the script for files listed in the files.txt file specified ate input/PARS folder and exit. The file.txt must have only the file name (without path) of the files in each line.",
)

# Execute the parse_args() method
args = PARS_parser.parse_args()

# if args.date is None:
if not args.date:
    export_date = args.date
else:
    try:
        export_date = datetime.strptime(args.date, "%d/%m/%Y")
    except:
        PARS_parser.error("Bad date format, see --help to further information")

# check if there is at least one action requested
if args.standard is None and args.list is None:
    PARS_parser.error("No action requested, see --help to further information")

if args.standard is not None and args.list is not None:
    PARS_parser.error("Invalid action requested, see --help to further information")

# ##################### SCRIPT #####################


# Folders and files path
path_cwd = pathlib.Path.cwd().joinpath("PARS")

print(path_cwd.name)

# if path_cwd.name != "PARS":
#     print(
#         "ERRO. Please make sure python current working directory is the /PARS folder which contains this script"
#     )
#     print("ERRO. Current working directory is:", path_cwd)
#     quit()

path_input = path_cwd.joinpath("input", "PARS")
path_input_data = path_input.joinpath("data")
path_input_support = path_input.joinpath("support")

path_output = path_cwd.joinpath("output", "PARS")
path_output_data = path_output.joinpath("netCDF")

# reading auxiliar data
with open(path_input_support.joinpath("variables_info.json"), "r") as xfile:
    variables_info_file = xfile.read()
variables_info = json.loads(variables_info_file)

# files
EXT = ""
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

# for each file
while True:
    day_data, export_date, flag_date = utils.parse_files(
        files, export_date, variables_info
    )

    if flag_date:
        print("fim")
        break
    else:
        print("continua")

    if day_data.shape[0] != 0:

        cdf_filename = (
            "att"
            + "laserdisd"
            + "cam."
            + "b0."
            + day_data.index[0].strftime("%Y%m%d.%H%M%S")
            + ".nc"
        )

        utils.generate_netCDF(
            cdf_filename,
            day_data,
            variables_info,
            netCDF_info,
            path_input,
            path_output_data,
        )

        print("")

        if args.date:
            break


# get variables
