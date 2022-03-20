from datetime import datetime, timedelta
import os
from glob import glob
import pandas as pd
import numpy as np
from netCDF4 import Dataset
import time
import json


###############################################################################################################################


def generate_netCDF(
    selected, datetime_for_lines, data_per_var, all_var_list, widths_str
):
    # sourcery skip: list-comprehension, move-assign
    # creating the attributes and general variables (time, base_time, time_offset) for the netCDF file

    datetime_for_lines_sorted = sort_datetime_for_lines(datetime_for_lines)

    init_datetime = datetime_for_lines_sorted[0]
    final_datetime = datetime_for_lines_sorted[len(datetime_for_lines_sorted) - 1]

    #     init_datetime = datetime_for_lines_sorted[0].replace(hour=0, minute=0, second=0)
    #     final_datetime = init_datetime
    #     final_datetime += timedelta(days=1)

    #     if selected == "ave":
    #         datetime_range = pd.date_range(
    #             start=init_datetime, end=final_datetime, freq="1min"
    #         )
    #     else:
    #         datetime_range = pd.date_range(
    #             start=init_datetime, end=final_datetime, freq="10s"
    #         )

    midnight_aux = init_datetime.replace(hour=0, minute=0, second=0)

    time_for_netCDF = []
    for i in range(len(datetime_for_lines_sorted)):
        time_for_netCDF.append(
            np.float32((datetime_for_lines_sorted[i] - midnight_aux).total_seconds())
        )

    time_offset_for_netCDF = []
    for i in range(len(datetime_for_lines_sorted)):
        time_offset_for_netCDF.append(
            np.float32((datetime_for_lines_sorted[i] - init_datetime).total_seconds())
        )

    if selected == "raw":
        Fnn_data = stack_var_nn("F", data_per_var, all_var_list)
    else:
        Fnn_data = stack_var_nn("F", data_per_var, all_var_list)
        Dnn_data = stack_var_nn("D", data_per_var, all_var_list)
        Nnn_data = stack_var_nn("N", data_per_var, all_var_list)

    cdf_filename = (
        "att"
        + "mrr"
        + "cam."
        + "b0."
        + init_datetime.strftime("%Y%m%d.%H%M%S")
        + "."
        + selected
        + ".nc"
    )

    with open("./input/MRR/netCDF_info.json", "r") as xfile:
        netCDF_info_file = xfile.read()

    netCDF_info = json.loads(netCDF_info_file)

    # generating the netCDF file
    output_folder = "output/MRR/netCDF"

    # check if file already exists, if true delete
    if os.path.exists("./" + output_folder + "/" + cdf_filename):
        os.remove("./" + output_folder + "/" + cdf_filename)
        print("File already exists, overwriting a new one...")

    print("Generating netCDF: " + cdf_filename)
    MRR_CDF = Dataset("./" + output_folder + "/" + cdf_filename, "w", format="NETCDF4")

    #################### GLOBAL ATTRIBUTES #######################

    MRR_CDF.description = netCDF_info["global"]["description"]
    # MRR_CDF.command_line = netCDF_info["global"]["command_line"]
    # MRR_CDF.conventions = netCDF_info["global"]["conventions"]
    # MRR_CDF.dod_version = netCDF_info["global"]["dod_version"]
    # MRR_CDF.input_source = netCDF_info["global"]["input_source"]
    MRR_CDF.site_id = netCDF_info["global"]["site_id"]
    MRR_CDF.platform_id = netCDF_info["global"]["platform_id"]
    MRR_CDF.facility_id = netCDF_info["global"]["facility_id"]
    MRR_CDF.data_level = netCDF_info["global"]["data_level"]
    MRR_CDF.location_description = netCDF_info["global"]["location_description"]
    MRR_CDF.datastream = netCDF_info["global"]["datastream"]
    MRR_CDF.serial_number = netCDF_info["global"]["serial_number"]
    MRR_CDF.sampling_interval = netCDF_info["global"]["sampling_interval"]
    MRR_CDF.averaging_interval = netCDF_info["global"]["averaging_interval"]
    # MRR_CDF.doi = netCDF_info["global"]["doi"]

    ######################## DIMENSIONS ##########################

    # variables dimensions
    profile = MRR_CDF.createDimension(
        netCDF_info["dimensions"]["profile"]["symbol"], len(widths_str[0]) - 1
    )
    Ndrop = MRR_CDF.createDimension(netCDF_info["dimensions"]["Ndrop"]["symbol"], 64)
    time = MRR_CDF.createDimension(
        netCDF_info["dimensions"]["time"]["symbol"], len(datetime_for_lines_sorted)
    )

    ######################## VARIABLES ###########################

    # variable: base_time (escalar)
    base_time = MRR_CDF.createVariable(
        netCDF_info["variables"]["base_time"]["symbol"], "u4"
    )  # u4 == 32-bit unsigned integer
    base_time.long_name = netCDF_info["variables"]["base_time"]["longname"]
    base_time.units = netCDF_info["variables"]["base_time"]["units"]
    base_time[:] = init_datetime.timestamp()

    # variable: time_offset
    time_offset = MRR_CDF.createVariable(
        netCDF_info["variables"]["time_offset"]["symbol"],
        "f4",
        (netCDF_info["dimensions"]["time"]["symbol"],),
    )
    time_offset.long_name = netCDF_info["variables"]["time_offset"]["longname"]
    time_offset.units = netCDF_info["variables"]["time_offset"]["units"]
    time_offset[:] = time_offset_for_netCDF

    # Variable: time
    time = MRR_CDF.createVariable(
        netCDF_info["variables"]["time"]["symbol"],
        "f4",
        (netCDF_info["dimensions"]["time"]["symbol"],),
    )
    time.long_name = netCDF_info["variables"]["time"]["longname"]
    time.units = netCDF_info["variables"]["time"]["units"]
    time[:] = time_for_netCDF

    # Variable: mdq
    mdq = MRR_CDF.createVariable(
        netCDF_info["variables"]["mdq"]["symbol"],
        "f4",
        (netCDF_info["dimensions"]["time"]["symbol"],),
    )
    mdq.long_name = netCDF_info["variables"]["mdq"]["longname"]
    mdq.units = netCDF_info["variables"]["mdq"]["units"]
    mdq.missing_value = float(netCDF_info["variables"]["mdq"]["missing_value"])
    mdq[:] = (
        data_per_var[all_var_list.index("MDQ")]
        .fillna(float(netCDF_info["variables"]["mdq"]["missing_value"]), inplace=False)
        .to_numpy()
        .astype("float32")
    )

    # Variable: height
    height = MRR_CDF.createVariable(
        netCDF_info["variables"]["height"]["symbol"],
        "f4",
        (
            netCDF_info["dimensions"]["time"]["symbol"],
            netCDF_info["dimensions"]["profile"]["symbol"],
        ),
    )
    height.long_name = netCDF_info["variables"]["height"]["longname"]
    height.units = netCDF_info["variables"]["height"]["units"]
    height.missing_value = float(netCDF_info["variables"]["height"]["missing_value"])
    height[:, :] = (
        data_per_var[all_var_list.index("H")]
        .fillna(
            float(netCDF_info["variables"]["height"]["missing_value"]), inplace=False
        )
        .to_numpy()
        .astype("float32")
    )

    # Variable: transfer function
    TF = MRR_CDF.createVariable(
        netCDF_info["variables"]["TF"]["symbol"],
        "f4",
        (
            netCDF_info["dimensions"]["time"]["symbol"],
            netCDF_info["dimensions"]["profile"]["symbol"],
        ),
    )
    TF.long_name = netCDF_info["variables"]["TF"]["longname"]
    TF.units = netCDF_info["variables"]["TF"]["units"]
    TF.missing_value = float(netCDF_info["variables"]["TF"]["missing_value"])
    TF[:, :] = (
        data_per_var[all_var_list.index("TF")]
        .fillna(float(netCDF_info["variables"]["TF"]["missing_value"]), inplace=False)
        .to_numpy()
        .astype("float32")
    )

    if selected == "raw":
        # Variable: Fnn
        Fnn = MRR_CDF.createVariable(
            netCDF_info["variables"]["Fnn"]["symbol"],
            "f4",
            (
                netCDF_info["dimensions"]["time"]["symbol"],
                netCDF_info["dimensions"]["profile"]["symbol"],
                netCDF_info["dimensions"]["Ndrop"]["symbol"],
            ),
        )
        Fnn.long_name = netCDF_info["variables"]["Fnn"]["longname"]
        Fnn.units = netCDF_info["variables"]["Fnn"]["units"]
        Fnn.missing_value = float(netCDF_info["variables"]["Fnn"]["missing_value"])
        Fnn[:, :, :] = Fnn_data

    else:
        # Variable: Fnn
        Fnn = MRR_CDF.createVariable(
            netCDF_info["variables"]["Fnn"]["symbol"],
            "f4",
            (
                netCDF_info["dimensions"]["time"]["symbol"],
                netCDF_info["dimensions"]["profile"]["symbol"],
                netCDF_info["dimensions"]["Ndrop"]["symbol"],
            ),
        )
        Fnn.long_name = netCDF_info["variables"]["Fnn"]["longname"]
        Fnn.units = netCDF_info["variables"]["Fnn"]["units"]
        Fnn.missing_value = float(netCDF_info["variables"]["Fnn"]["missing_value"])
        Fnn[:, :, :] = Fnn_data

        # Variable: Dnn
        Dnn = MRR_CDF.createVariable(
            netCDF_info["variables"]["Dnn"]["symbol"],
            "f4",
            (
                netCDF_info["dimensions"]["time"]["symbol"],
                netCDF_info["dimensions"]["profile"]["symbol"],
                netCDF_info["dimensions"]["Ndrop"]["symbol"],
            ),
        )
        Dnn.long_name = netCDF_info["variables"]["Dnn"]["longname"]
        Dnn.units = netCDF_info["variables"]["Dnn"]["units"]
        Dnn.missing_value = float(netCDF_info["variables"]["Dnn"]["missing_value"])
        Dnn[:, :, :] = Dnn_data

        # Variable: Nnn
        Nnn = MRR_CDF.createVariable(
            netCDF_info["variables"]["Nnn"]["symbol"],
            "f4",
            (
                netCDF_info["dimensions"]["time"]["symbol"],
                netCDF_info["dimensions"]["profile"]["symbol"],
                netCDF_info["dimensions"]["Ndrop"]["symbol"],
            ),
        )
        Nnn.long_name = netCDF_info["variables"]["Nnn"]["longname"]
        Nnn.units = netCDF_info["variables"]["Nnn"]["units"]
        Nnn.missing_value = float(netCDF_info["variables"]["Nnn"]["missing_value"])
        Nnn[:, :, :] = Nnn_data

        # Variable: PIA
        PIA = MRR_CDF.createVariable(
            netCDF_info["variables"]["PIA"]["symbol"],
            "f4",
            (
                netCDF_info["dimensions"]["time"]["symbol"],
                netCDF_info["dimensions"]["profile"]["symbol"],
            ),
        )
        PIA.long_name = netCDF_info["variables"]["PIA"]["longname"]
        PIA.units = netCDF_info["variables"]["PIA"]["units"]
        PIA.missing_value = float(netCDF_info["variables"]["PIA"]["missing_value"])
        PIA[:, :] = (
            data_per_var[all_var_list.index("PIA")]
            .fillna(
                float(netCDF_info["variables"]["PIA"]["missing_value"]), inplace=False
            )
            .to_numpy()
            .astype("float32")
        )

        # Variable: Z
        Z = MRR_CDF.createVariable(
            netCDF_info["variables"]["Z"]["symbol"],
            "f4",
            (
                netCDF_info["dimensions"]["time"]["symbol"],
                netCDF_info["dimensions"]["profile"]["symbol"],
            ),
        )
        Z.long_name = netCDF_info["variables"]["Z"]["longname"]
        Z.units = netCDF_info["variables"]["Z"]["units"]
        Z.missing_value = float(netCDF_info["variables"]["Z"]["missing_value"])
        Z[:, :] = (
            data_per_var[all_var_list.index("Z")]
            .fillna(
                float(netCDF_info["variables"]["Z"]["missing_value"]), inplace=False
            )
            .to_numpy()
            .astype("float32")
        )

        # Variable: z
        z = MRR_CDF.createVariable(
            netCDF_info["variables"]["z"]["symbol"],
            "f4",
            (
                netCDF_info["dimensions"]["time"]["symbol"],
                netCDF_info["dimensions"]["profile"]["symbol"],
            ),
        )
        z.long_name = netCDF_info["variables"]["z"]["longname"]
        z.units = netCDF_info["variables"]["z"]["units"]
        z.missing_value = float(netCDF_info["variables"]["z"]["missing_value"])
        z[:, :] = (
            data_per_var[all_var_list.index("z")]
            .fillna(
                float(netCDF_info["variables"]["z"]["missing_value"]), inplace=False
            )
            .to_numpy()
            .astype("float32")
        )

        # Variable: Rain Rate
        RR = MRR_CDF.createVariable(
            netCDF_info["variables"]["RR"]["symbol"],
            "f4",
            (
                netCDF_info["dimensions"]["time"]["symbol"],
                netCDF_info["dimensions"]["profile"]["symbol"],
            ),
        )
        RR.long_name = netCDF_info["variables"]["RR"]["longname"]
        RR.units = netCDF_info["variables"]["z"]["units"]
        RR.missing_value = float(netCDF_info["variables"]["RR"]["missing_value"])
        RR[:, :] = (
            data_per_var[all_var_list.index("RR")]
            .fillna(
                float(netCDF_info["variables"]["RR"]["missing_value"]), inplace=False
            )
            .to_numpy()
            .astype("float32")
        )

        # Variable: LWC
        LWC = MRR_CDF.createVariable(
            netCDF_info["variables"]["LWC"]["symbol"],
            "f4",
            (
                netCDF_info["dimensions"]["time"]["symbol"],
                netCDF_info["dimensions"]["profile"]["symbol"],
            ),
        )
        LWC.long_name = netCDF_info["variables"]["LWC"]["longname"]
        LWC.units = netCDF_info["variables"]["LWC"]["units"]
        LWC.missing_value = float(netCDF_info["variables"]["LWC"]["missing_value"])
        LWC[:, :] = (
            data_per_var[all_var_list.index("LWC")]
            .fillna(
                float(netCDF_info["variables"]["LWC"]["missing_value"]), inplace=False
            )
            .to_numpy()
            .astype("float32")
        )

        # Variable: W
        W = MRR_CDF.createVariable(
            netCDF_info["variables"]["W"]["symbol"],
            "f4",
            (
                netCDF_info["dimensions"]["time"]["symbol"],
                netCDF_info["dimensions"]["profile"]["symbol"],
            ),
        )
        W.long_name = netCDF_info["variables"]["W"]["longname"]
        W.units = netCDF_info["variables"]["W"]["units"]
        W.missing_value = float(netCDF_info["variables"]["W"]["missing_value"])
        W[:, :] = (
            data_per_var[all_var_list.index("W")]
            .fillna(
                float(netCDF_info["variables"]["W"]["missing_value"]), inplace=False
            )
            .to_numpy()
            .astype("float32")
        )

    # variable: lat (escalar)
    lat = MRR_CDF.createVariable(
        netCDF_info["variables"]["lat"]["symbol"], "u4"
    )  # u4 == 32-bit unsigned integer
    lat.long_name = netCDF_info["variables"]["lat"]["longname"]
    lat.units = netCDF_info["variables"]["lat"]["units"]
    lat[:] = float(netCDF_info["variables"]["lat"]["value"])

    # variable: lon (escalar)
    lon = MRR_CDF.createVariable(
        netCDF_info["variables"]["lon"]["symbol"], "u4"
    )  # u4 == 32-bit unsigned integer
    lon.long_name = netCDF_info["variables"]["lon"]["longname"]
    lon.units = netCDF_info["variables"]["lon"]["units"]
    lon[:] = float(netCDF_info["variables"]["lon"]["value"])

    # variable: Altitude (escalar)
    alt = MRR_CDF.createVariable(
        netCDF_info["variables"]["alt"]["symbol"], "u4"
    )  # u4 == 32-bit unsigned integer
    alt.long_name = netCDF_info["variables"]["alt"]["longname"]
    alt.units = netCDF_info["variables"]["alt"]["units"]
    alt[:] = float(netCDF_info["variables"]["alt"]["value"])

    ########################### CLOSING FILE ##################################

    MRR_CDF.close()

    print("Generated netCDF: " + cdf_filename)
    print(" ")

    # register what file has been generated
    creation_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("./output/MRR/MRR_netCDF.log", "a") as f:
        f.write(creation_datetime + "|" + cdf_filename + "\n")


###############################################################################################################################


def process_ave_files(selected, files, all_var_list):

    # acquiring data from the files
    [widths_str, param_numbers_list] = read_param(selected, files)

    data = [[] for i in range(len(files))]

    MRR_pos_per_file = [[] for i in range(len(files))]

    if check_param(widths_str, param_numbers_list):
        data[0] = pd.read_fwf(files[0], widths=widths_str[0], header=None)
        MRR_pos_per_file[0] = find_var(data[0], "MRR")

        print("File read: 0")
        for i in range(1, len(files)):
            data[i] = pd.read_fwf(files[i], widths=widths_str[0], header=None)
            set_columns(data[i])
            MRR_pos_per_file[i] = find_var(data[i], "MRR")

            print("File read:", i)

    datetime_for_lines = get_datetime_for_lines(files, MRR_pos_per_file)

    print("Processing variables data")
    data_per_var = [
        export_var(
            "ave",
            all_var_list[i],
            data,
            files,
            datetime_for_lines,
            MRR_pos_per_file,
        )
        for i in range(len(all_var_list))
    ]

    print("All variables exported")

    return [datetime_for_lines, data_per_var, widths_str]


###############################################################################################################################


def process_pro_files(selected, files, all_var_list):

    # acquiring data from the files
    [widths_str, param_numbers_list] = read_param(selected, files)

    data = [[] for i in range(len(files))]

    MRR_pos_per_file = [[] for i in range(len(files))]

    if check_param(widths_str, param_numbers_list):
        data[0] = pd.read_fwf(files[0], widths=widths_str[0], header=None)
        MRR_pos_per_file[0] = find_var(data[0], "MRR")

        print("File read: 0")
        for i in range(1, len(files)):
            data[i] = pd.read_fwf(files[i], widths=widths_str[0], header=None)
            set_columns(data[i])
            MRR_pos_per_file[i] = find_var(data[i], "MRR")

            print("File read:", i)

    datetime_for_lines = get_datetime_for_lines(files, MRR_pos_per_file)

    print("Processing variables data")
    data_per_var = [
        export_var(
            "pro",
            all_var_list[i],
            data,
            files,
            datetime_for_lines,
            MRR_pos_per_file,
        )
        for i in range(len(all_var_list))
    ]

    print("All variables exported")

    return [datetime_for_lines, data_per_var, widths_str]


###############################################################################################################################


def process_raw_files(selected, files, all_var_list):

    # acquiring data from the files
    [widths_str, param_numbers_list] = read_param(selected, files)

    data = [[] for i in range(len(files))]

    MRR_pos_per_file = [[] for i in range(len(files))]

    if check_param(widths_str, param_numbers_list):
        data[0] = pd.read_fwf(files[0], widths=widths_str[0], header=None)
        MRR_pos_per_file[0] = find_var(data[0], "MRR")

        print("File read: 0")
        for i in range(1, len(files)):
            data[i] = pd.read_fwf(files[i], widths=widths_str[0], header=None)
            set_columns(data[i])
            MRR_pos_per_file[i] = find_var(data[i], "MRR")

            print("File read:", i)

    datetime_for_lines = get_datetime_for_lines(files, MRR_pos_per_file)

    print("Processing variables data")
    data_per_var = [
        export_var(
            "raw",
            all_var_list[i],
            data,
            files,
            datetime_for_lines,
            MRR_pos_per_file,
        )
        for i in range(len(all_var_list))
    ]

    print("All variables exported")

    return [datetime_for_lines, data_per_var, widths_str]


###############################################################################################################################


def read_param(selected, files):
    widths_str = [[] for i in range(len(files))]
    param_numbers_list = [[] for i in range(len(files))]

    for j in range(len(files)):
        f = open(files[j], "r")
        next(f)
        param = f.readline()
        param_numbers = [int(word) for word in param.split() if word.isdigit()]
        widths_str[j] = [3]

        param_numbers_list[j] = param_numbers

        for param_number in param_numbers:
            if selected == "raw":
                widths_str[j].append(9)
            else:
                widths_str[j].append(7)
    return [widths_str, param_numbers_list]


def check_param(widths_str, param_numbers_list):
    sizes = [len(widths_str[0])]
    for i in range(1, len(widths_str)):
        sizes.append(len(widths_str[i]))
    if any(x != sizes[0] for x in sizes):
        print("** Different number of columns in one/more files! **")
        for j in range(len(sizes)):
            print("File ", j, " number of columns: ", str(sizes[j]))
    else:
        flag = sum(
            param_numbers_list[i] != param_numbers_list[i + 1]
            for i in range(len(param_numbers_list) - 1)
        )

        if flag == 0:
            # print('## All files have the same columns! ##')
            return True
        print("** Different columns in one/more files! **")
        for j in range(len(sizes)):
            print("File ", j, " columns: ", param_numbers_list[j])
    return False


def find_var(data, str_var):
    return data[data.iloc[:, 0] == str_var].index.values


def set_columns(data):
    col_names = data.loc[1]
    col_names = col_names.values.tolist()
    data.columns = col_names


def get_datetime_for_lines(files, MRR_pos_per_file):
    headers = [[] for i in range(len(files))]

    for i in range(len(files)):
        f = open(files[i], "r")
        for position, line in enumerate(f):
            if position in MRR_pos_per_file[i]:
                headers[i].append(line)

    for header in headers:
        for j in range(len(header)):
            header[j] = header[j][4:16]

    datetime_for_lines = [[] for i in range(len(headers))]

    for i in range(len(headers)):
        for j in range(len(headers[i])):
            datetime_for_lines[i].append(
                datetime.strptime(headers[i][j], "%y%m%d%H%M%S")
            )  # YYMMDDhhmmss
    for i in range(len(datetime_for_lines)):
        datetime_for_lines[i] = pd.to_datetime(datetime_for_lines[i])

    return datetime_for_lines


def sort_datetime_for_lines(datetime_for_lines):
    datetime_for_lines_sorted = datetime_for_lines[0]
    for i in range(1, len(datetime_for_lines)):
        datetime_for_lines_sorted = datetime_for_lines_sorted.union(
            datetime_for_lines[i]
        )

    return datetime_for_lines_sorted.sort_values()


def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1


def build_dates_for_var(var_str, files, data, datetime_for_lines, MRR_pos_per_file):
    var_pos_per_file = [[] for i in range(len(files))]
    for i in range(len(files)):
        var_pos_per_file[i] = find_var(data[i], var_str)

    datetime_for_lines_var = [[] for i in range(len(files))]

    for i in range(len(files)):
        for j in range(len(var_pos_per_file[i])):
            if j < len(var_pos_per_file[i]) - 1:
                if (
                    MRR_pos_per_file[i][j]
                    + abs(MRR_pos_per_file[i][j] - MRR_pos_per_file[i][j + 1])
                ) > var_pos_per_file[i][j]:
                    datetime_for_lines_var[i].append(datetime_for_lines[i][j])
            else:
                if (
                    MRR_pos_per_file[i][j]
                    + abs(MRR_pos_per_file[i][j] - file_len(files[i]))
                ) > var_pos_per_file[i][j]:
                    datetime_for_lines_var[i].append(
                        datetime_for_lines[i][len(MRR_pos_per_file[len(files) - 1]) - 1]
                    )

    return datetime_for_lines_var


def export_var(selected, var_str, data, files, datetime_for_lines, MRR_pos_per_file):

    if var_str == "MDQ":
        datetime_for_lines_var = build_dates_for_var(
            "MRR", files, data, datetime_for_lines, MRR_pos_per_file
        )
        # extraindo a variável mdq
        mdq_data_aux = [[] for i in range(len(files))]
        for i in range(len(data)):
            mdq_data_aux[i] = data[i][data[i].iloc[:, 0] == "MRR"]

        mdq_data = [[] for i in range(len(files))]
        for i in range(len(mdq_data)):
            for j in range(len(mdq_data_aux[i])):
                mdq_data[i].append(["MDQ", mdq_data_aux[i].iloc[j, 16][4:7]])

        mdq_df = [[] for i in range(len(files))]
        for i in range(len(mdq_df)):
            mdq_df[i] = pd.DataFrame(mdq_data[i])

        var_data = [[] for i in range(len(files))]
        for i in range(len(var_data)):
            var_data[i] = mdq_df[i]
            var_data[i].insert(0, "Datetime (UTC)", datetime_for_lines_var[i])
            var_data[i] = var_data[i].set_index("Datetime (UTC)")
    else:
        datetime_for_lines_var = build_dates_for_var(
            var_str, files, data, datetime_for_lines, MRR_pos_per_file
        )
        # extraindo as variáveis
        var_data = [[] for i in range(len(files))]
        for i in range(len(files)):
            var_data[i] = data[i][data[i].iloc[:, 0] == var_str]

            var_data[i].insert(0, "Datetime (UTC)", datetime_for_lines_var[i])
            var_data[i] = var_data[i].set_index("Datetime (UTC)")

    var_data_total = var_data[0]
    for i in range(1, len(var_data)):
        var_data_total = pd.concat([var_data_total, var_data[i]])

    var_data_total = var_data_total.sort_index()

    var_data_total = var_data_total.drop(var_data_total.columns[0], axis=1)

    datetime_for_lines_sorted = sort_datetime_for_lines(datetime_for_lines)

    # essa parte de exportar os dados seria no nível dois
    # init_datetime = datetime_for_lines_sorted[0].replace(hour=0, minute=0, second=0)
    # final_datetime = init_datetime

    # Deixar só até 23:59
    # final_datetime += timedelta(days=1)

    # if selected == "ave":
    #     datetime_range = pd.date_range(
    #         start=init_datetime, end=final_datetime, freq="1min"
    #     )
    #     if var_str == "H":
    #         var_data_total = var_data_total.reindex(
    #             datetime_range, fill_value=np.nan, method="nearest"
    #         )
    #     else:
    #         var_data_total = var_data_total.reindex(
    #             datetime_range, fill_value=np.nan, method="nearest", tolerance="30s"
    #         )
    # elif selected == "pro":
    #     datetime_range = pd.date_range(
    #         start=init_datetime, end=final_datetime, freq="10s"
    #     )
    #     if var_str == "H":
    #         var_data_total = var_data_total.reindex(
    #             datetime_range, fill_value=np.nan, method="nearest"
    #         )
    #     else:
    #         var_data_total = var_data_total.reindex(
    #             datetime_range, fill_value=np.nan, method="nearest", tolerance="5s"
    #         )

    print("Exported " + var_str, end="\r")

    return var_data_total


def stack_var_nn(var_letter, data_per_var, all_var_list):
    var_str_list = [var_letter + "%02d" % x for x in range(64)]
    data_per_var_nn_numpy = [
        data_per_var[all_var_list.index(varstr)]
        .fillna(-999.0, inplace=False)
        .to_numpy()
        .astype("float32")
        for varstr in var_str_list
    ]

    return np.stack(data_per_var_nn_numpy, axis=-1)
