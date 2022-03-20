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

# files

# for each file
variable_comp = []
missing_comp = []
for block_idx, block in enumerate(blocks):
    variables = []
    var_missing = []
    aux = [item[0] for item in block]
    for var in interest_variables:
        if var in aux:
            idx = aux.index(var)
            if var == 1:
                variables += [utils.parse_ri(block[idx][1])]
            elif var == 7:
                variables += [utils.parse_z(block[idx][1])]
            elif var == 9:
                variables += [utils.parse_sample_interval(block[idx][1])]
            elif var == 13:
                utils.parse_serial(block[idx][1])
            elif var == 20:
                time_aux = block[idx][1]
            elif var == 21:
                date_aux = block[idx][1]
                variables += [utils.parse_datetime(f"{date_aux} {time_aux}")]
            elif var == 25:
                variables += [utils.parse_erro(block[idx][1])]
            elif var == 93:
                variables += [utils.parse_vol_p_diam(block[idx][1])]
        else:
            variables += [np.NaN]
            var_missing += [var]

    if var_missing:
        missing_comp += [(block_idx, var_missing)]

    variable_comp.append(variables)


# get variables
