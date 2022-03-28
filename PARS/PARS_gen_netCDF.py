# Folders and files path
path_cwd = pathlib.Path.cwd()

print(path_cwd.name)

if path_cwd.name != "PARS":
    print(
        "ERRO. Please make sure python current working directory is the /PARS folder which contains this script"
    )
    print("ERRO. Current working directory is:", path_cwd)
    quit()

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

# for each file
utils.process_files(files, export_date, variables_info)


# get variables
