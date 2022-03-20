import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import math
import pathlib
import os
from netCDF4 import Dataset
from netCDF4 import stringtochar


def process_files(files, columns, export_date, variables_info):

    joss_date_parser = lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S")

    # data is a list of dataframes containg the data from each file
    data = [
        pd.read_csv(
            file,
            sep="\s",
            header=None,
            names=columns,
            skiprows=[0],
            index_col=[0],
            parse_dates=[[0, 1]],
            date_parser=joss_date_parser,
            decimal=",",
            dtype={"RI": np.float64, "RA": np.float64, "RAT": np.float64},
            engine="python",
        )
        for file in files
    ]

    # all data receives the data from all files
    all_data = pd.concat(data).sort_index()

    aux_datetime = all_data.index[-1]

    if export_date == None:
        export_date = all_data.index[0]

    # selecionar a janela com o dia a ser exportado
    start_date = datetime(export_date.year, export_date.month, export_date.day, 0, 0)

    if variables_info["integration_time"] < 60:
        end_date = datetime(
            export_date.year,
            export_date.month,
            export_date.day,
            23,
            59,
            60 - variables_info["integration_time"] % 60,
        )
    elif variables_info["integration_time"] == 60:
        end_date = datetime(
            export_date.year, export_date.month, export_date.day, 23, 59
        )
    else:
        end_date = datetime(
            export_date.year,
            export_date.month,
            export_date.day,
            23,
            60 - math.floor(variables_info["integration_time"] / 60),
            60 - variables_info["integration_time"] % 60,
        )

    day_idx = pd.date_range(
        start=start_date,
        end=end_date,
        freq=str(variables_info["integration_time"]) + "S",
    )

    all_data = all_data.reindex(day_idx, fill_value=variables_info["missing_value"])

    # retornar o dataframe com dados do dia
    return (
        export_date + timedelta(days=1),
        all_data.loc[start_date:end_date],
        start_date > aux_datetime,
    )


# data is day_data[variables_info["drop_size"]]
# t is variables_info["integration_time"]
def get_ri(data, drop_size, mean_diam, velocity, t):

    c = (math.pi * 3.6) / (6 * pow(10, 3) * 0.005 * t)

    ri = []
    for idx, row in data.iterrows():
        r = c * sum(
            (row[n] * pow(diam, 3))
            for n, diam, vel in zip(drop_size, mean_diam, velocity)
        )
        ri.append(r)

    return ri


def get_ra(ri_data, t):
    return [ri * t / 3600 for ri in ri_data]


def get_rat(ra_data):
    return [sum(ra_data[0:i]) for i in range(len(ra_data))]


# data is day_data[variables_info["drop_size"]]
# t is variables_info["integration_time"]
def get_lwc(data, drop_size, mean_diam, velocity, t):

    c = math.pi / (6 * 0.005 * t)

    lwc = []
    for idx, row in data.iterrows():
        r = c * sum(
            (row[n] * pow(diam, 3)) / vel
            for n, diam, vel in zip(drop_size, mean_diam, velocity)
        )
        lwc.append(r)

    return lwc


# data is day_data[variables_info["drop_size"]]
def get_z(data, drop_size, mean_diam, velocity, t):

    c = 1 / (0.005 * t)

    z = []
    for idx, row in data.iterrows():
        r = c * sum(
            (row[n] * pow(diam, 6)) / vel
            for n, diam, vel in zip(drop_size, mean_diam, velocity)
        )
        z.append(r)

    return z


# z_data is the list produced by get_z() function
def get_zdb(z_data):
    return [10 * math.log(z, 10) if z > 0 else 0 for z in z_data]


def get_ek(data, drop_size, mean_diam, velocity):

    c = math.pi / (12 * 0.005 * pow(10, 6))

    ek = []
    for idx, row in data.iterrows():
        r = c * sum(
            row[n] * pow(diam, 3) * pow(vel, 2)
            for n, diam, vel in zip(drop_size, mean_diam, velocity)
        )
        ek.append(r)

    return ek


# ek_data is the list produced by get_ek() function
def get_ef(ek_data, t):
    return [ek * 3600 / t for ek in ek_data]


def get_n_0(lwc_data, z_data):

    c = (1 / math.pi) * pow((math.factorial(6) / math.pi), 4 / 3)

    return [
        c * lwc * pow(lwc / z, 4 / 3) if z != 0 else 0
        for lwc, z in zip(lwc_data, z_data)
    ]


def get_slope(lwc_data, z_data):

    c = math.factorial(6) / math.pi

    return [
        pow(c * lwc / z, 1 / 3) if z != 0 else 0 for lwc, z in zip(lwc_data, z_data)
    ]


# data is day_data[variables_info["drop_size"]]
def get_d_max(data):
    return [row.max() for idx, row in data.iterrows()]


def get_n_d(data, drop_size, delta_diam, velocity, t):

    c = 1 / (math.pi * t)

    n_d = []
    for idx, row in data.iterrows():
        n_d_i = [
            row[n] / (vel * ddiam)
            for n, ddiam, vel in zip(drop_size, delta_diam, velocity)
        ]
        n_d.append(n_d_i)

    return n_d


def string2ascii_array(string):
    ascii_array = [np.int64(ord(char)) for char in string]
    ascii_array.extend([np.int64(0) for i in range(255 - len(ascii_array))])
    return np.array(ascii_array)


def generate_netCDF(
    cdf_filename,
    day_data,
    columns,
    variables_info,
    netCDF_info,
    path_input,
    path_output_data,
):

    print("Generating netCDF:", cdf_filename)

    # check if file already exists, if true delete
    if os.path.exists(path_output_data.joinpath(cdf_filename)):
        os.remove(path_output_data.joinpath(cdf_filename))
        print("File already exists, overwriting a new one...")

    JOSS_CDF = Dataset(path_output_data.joinpath(cdf_filename), "w", format="NETCDF4")

    # ######################## DIMENSIONS ##########################

    drop_class = JOSS_CDF.createDimension(
        netCDF_info["dimensions"]["drop_class"]["symbol"], 20
    )

    time = JOSS_CDF.createDimension(
        netCDF_info["dimensions"]["time"]["symbol"], day_data.shape[0]
    )

    str_dim = JOSS_CDF.createDimension("str_dim", 255)

    # ######################## GLOBAL VARIABLES ###########################

    # variable: data_description
    data_description = JOSS_CDF.createVariable(
        netCDF_info["global"]["data_description"]["name"], "u8", ("str_dim",)
    )
    data_description[:] = string2ascii_array(
        netCDF_info["global"]["data_description"]["value"]
    )

    data_description.shortname = netCDF_info["global"]["data_description"]["shortname"]
    data_description.description = netCDF_info["global"]["data_description"][
        "description"
    ]
    data_description.unit = netCDF_info["global"]["data_description"]["unit"]
    data_description.datatype = netCDF_info["global"]["data_description"]["datatype"]
    data_description.id = netCDF_info["global"]["data_description"]["id"]
    data_description.optional = netCDF_info["global"]["data_description"]["optional"]

    # variable: site_id
    site_id = JOSS_CDF.createVariable(
        netCDF_info["global"]["site_identifier"]["name"], "u8"
    )
    site_id[:] = np.int64(netCDF_info["global"]["site_identifier"]["value"])

    site_id.shortname = netCDF_info["global"]["site_identifier"]["shortname"]
    site_id.description = netCDF_info["global"]["site_identifier"]["description"]
    site_id.unit = netCDF_info["global"]["site_identifier"]["unit"]
    site_id.datatype = netCDF_info["global"]["site_identifier"]["datatype"]
    site_id.id = netCDF_info["global"]["site_identifier"]["id"]
    site_id.optional = netCDF_info["global"]["site_identifier"]["optional"]

    # variable: platform_id
    platform_id = JOSS_CDF.createVariable(
        netCDF_info["global"]["platform_identifier"]["name"], "u8"
    )
    platform_id[:] = np.int64(netCDF_info["global"]["platform_identifier"]["value"])

    platform_id.shortname = netCDF_info["global"]["platform_identifier"]["shortname"]
    platform_id.description = netCDF_info["global"]["platform_identifier"][
        "description"
    ]
    platform_id.unit = netCDF_info["global"]["platform_identifier"]["unit"]
    platform_id.datatype = netCDF_info["global"]["platform_identifier"]["datatype"]
    platform_id.id = netCDF_info["global"]["platform_identifier"]["id"]
    platform_id.optional = netCDF_info["global"]["platform_identifier"]["optional"]

    # variable: facility_id
    facility_id = JOSS_CDF.createVariable(
        netCDF_info["global"]["facility_identifier"]["name"], "u8"
    )
    facility_id[:] = np.int64(netCDF_info["global"]["facility_identifier"]["value"])

    facility_id.shortname = netCDF_info["global"]["facility_identifier"]["shortname"]
    facility_id.description = netCDF_info["global"]["facility_identifier"][
        "description"
    ]
    facility_id.unit = netCDF_info["global"]["facility_identifier"]["unit"]
    facility_id.datatype = netCDF_info["global"]["facility_identifier"]["datatype"]
    facility_id.id = netCDF_info["global"]["facility_identifier"]["id"]
    facility_id.optional = netCDF_info["global"]["facility_identifier"]["optional"]

    # variable: data_level
    data_level = JOSS_CDF.createVariable(
        netCDF_info["global"]["data_level"]["name"], "u8"
    )
    data_level[:] = np.int64(netCDF_info["global"]["data_level"]["value"])

    data_level.shortname = netCDF_info["global"]["data_level"]["shortname"]
    data_level.description = netCDF_info["global"]["data_level"]["description"]
    data_level.unit = netCDF_info["global"]["data_level"]["unit"]
    data_level.datatype = netCDF_info["global"]["data_level"]["datatype"]
    data_level.id = netCDF_info["global"]["data_level"]["id"]
    data_level.optional = netCDF_info["global"]["data_level"]["optional"]

    # variable: location
    location = JOSS_CDF.createVariable(netCDF_info["global"]["location"]["name"], "u8")
    location[:] = np.int64(netCDF_info["global"]["location"]["value"])

    location.shortname = netCDF_info["global"]["location"]["shortname"]
    location.description = netCDF_info["global"]["location"]["description"]
    location.unit = netCDF_info["global"]["location"]["unit"]
    location.datatype = netCDF_info["global"]["location"]["datatype"]
    location.id = netCDF_info["global"]["location"]["id"]
    location.optional = netCDF_info["global"]["location"]["optional"]

    variable: datastream
    datastream = JOSS_CDF.createVariable(
        netCDF_info["global"]["datastream"]["name"], "u8", ("str_dim",)
    )
    datastream[:] = string2ascii_array(netCDF_info["global"]["datastream"]["value"])

    datastream.shortname = netCDF_info["global"]["datastream"]["shortname"]
    datastream.description = netCDF_info["global"]["datastream"]["description"]
    datastream.unit = netCDF_info["global"]["datastream"]["unit"]
    datastream.datatype = netCDF_info["global"]["datastream"]["datatype"]
    datastream.id = netCDF_info["global"]["datastream"]["id"]
    datastream.optional = netCDF_info["global"]["datastream"]["optional"]

    # variable: samp_interval
    samp_interval = JOSS_CDF.createVariable(
        netCDF_info["global"]["sampling_interval"]["name"], "f8"
    )
    samp_interval[:] = np.float64(netCDF_info["global"]["sampling_interval"]["value"])

    samp_interval.shortname = netCDF_info["global"]["sampling_interval"]["shortname"]
    samp_interval.description = netCDF_info["global"]["sampling_interval"][
        "description"
    ]
    samp_interval.unit = netCDF_info["global"]["sampling_interval"]["unit"]
    samp_interval.datatype = netCDF_info["global"]["sampling_interval"]["datatype"]
    samp_interval.id = netCDF_info["global"]["sampling_interval"]["id"]
    samp_interval.optional = netCDF_info["global"]["sampling_interval"]["optional"]

    # variable: avar_interval
    avar_interval = JOSS_CDF.createVariable(
        netCDF_info["global"]["averaging_interval"]["name"], "f8"
    )
    avar_interval[:] = np.float64(netCDF_info["global"]["averaging_interval"]["value"])

    avar_interval.shortname = netCDF_info["global"]["averaging_interval"]["shortname"]
    avar_interval.description = netCDF_info["global"]["averaging_interval"][
        "description"
    ]
    avar_interval.unit = netCDF_info["global"]["averaging_interval"]["unit"]
    avar_interval.datatype = netCDF_info["global"]["averaging_interval"]["datatype"]
    avar_interval.id = netCDF_info["global"]["averaging_interval"]["id"]
    avar_interval.optional = netCDF_info["global"]["averaging_interval"]["optional"]

    # variable: serial_number
    serial_number = JOSS_CDF.createVariable(
        netCDF_info["global"]["serial_number"]["name"], "u8"
    )
    serial_number[:] = np.int64(netCDF_info["global"]["serial_number"]["value"])

    serial_number.shortname = netCDF_info["global"]["serial_number"]["shortname"]
    serial_number.description = netCDF_info["global"]["serial_number"]["description"]
    serial_number.unit = netCDF_info["global"]["serial_number"]["unit"]
    serial_number.datatype = netCDF_info["global"]["serial_number"]["datatype"]
    serial_number.id = netCDF_info["global"]["serial_number"]["id"]
    serial_number.optional = netCDF_info["global"]["serial_number"]["optional"]

    # variable: calibration_date
    calibration_date = JOSS_CDF.createVariable(
        netCDF_info["global"]["calibration_date"]["name"], "u8"
    )
    calibration_date[:] = np.datetime64(
        netCDF_info["global"]["calibration_date"]["value"]
    )

    calibration_date.shortname = netCDF_info["global"]["calibration_date"]["shortname"]
    calibration_date.description = netCDF_info["global"]["calibration_date"][
        "description"
    ]
    calibration_date.unit = netCDF_info["global"]["calibration_date"]["unit"]
    calibration_date.datatype = netCDF_info["global"]["calibration_date"]["datatype"]
    calibration_date.id = netCDF_info["global"]["calibration_date"]["id"]
    calibration_date.optional = netCDF_info["global"]["calibration_date"]["optional"]

    # variable: lat
    lat = JOSS_CDF.createVariable(netCDF_info["global"]["lat"]["name"], "u8")
    lat[:] = np.float64(netCDF_info["global"]["lat"]["value"])

    lat.shortname = netCDF_info["global"]["lat"]["shortname"]
    lat.description = netCDF_info["global"]["lat"]["description"]
    lat.unit = netCDF_info["global"]["lat"]["unit"]
    lat.datatype = netCDF_info["global"]["lat"]["datatype"]
    lat.id = netCDF_info["global"]["lat"]["id"]
    lat.optional = netCDF_info["global"]["lat"]["optional"]

    # variable: lon
    lon = JOSS_CDF.createVariable(netCDF_info["global"]["lon"]["name"], "u8")
    lon[:] = np.float64(netCDF_info["global"]["lon"]["value"])

    lon.shortname = netCDF_info["global"]["lon"]["shortname"]
    lon.description = netCDF_info["global"]["lon"]["description"]
    lon.unit = netCDF_info["global"]["lon"]["unit"]
    lon.datatype = netCDF_info["global"]["lon"]["datatype"]
    lon.id = netCDF_info["global"]["lon"]["id"]
    lon.optional = netCDF_info["global"]["lon"]["optional"]

    # variable: alt
    alt = JOSS_CDF.createVariable(netCDF_info["global"]["alt"]["name"], "u8")
    alt[:] = np.float64(netCDF_info["global"]["alt"]["value"])

    alt.shortname = netCDF_info["global"]["alt"]["shortname"]
    alt.description = netCDF_info["global"]["alt"]["description"]
    alt.unit = netCDF_info["global"]["alt"]["unit"]
    alt.datatype = netCDF_info["global"]["alt"]["datatype"]
    alt.id = netCDF_info["global"]["alt"]["id"]
    alt.optional = netCDF_info["global"]["alt"]["optional"]

    # ######################## TIME VARIABLES ###########################

    # variable: base_time
    base_time = JOSS_CDF.createVariable(
        netCDF_info["variables"]["base_time"]["name"], "u8"
    )
    # u8 == 32-bit unsigned integer
    base_time[:] = np.int64(day_data.index[0].timestamp())

    base_time.shortname = netCDF_info["variables"]["base_time"]["shortname"]
    base_time.description = netCDF_info["variables"]["base_time"]["description"]
    base_time.unit = netCDF_info["variables"]["base_time"]["unit"]
    base_time.datatype = netCDF_info["variables"]["base_time"]["datatype"]
    base_time.id = netCDF_info["variables"]["base_time"]["id"]
    base_time.optional = netCDF_info["variables"]["base_time"]["optional"]

    # variable: time_offset
    time_offset = JOSS_CDF.createVariable(
        netCDF_info["variables"]["time_offset"]["name"],
        "f8",
        (netCDF_info["dimensions"]["time"]["symbol"],),
    )
    time_offset[:] = (
        (day_data.index - day_data.index[0])
        .map(lambda x: x.total_seconds())
        .to_numpy()
        .astype("float64")
    )

    time_offset.shortname = netCDF_info["variables"]["time_offset"]["shortname"]
    time_offset.description = netCDF_info["variables"]["time_offset"]["description"]
    time_offset.unit = netCDF_info["variables"]["time_offset"]["unit"]
    time_offset.datatype = netCDF_info["variables"]["time_offset"]["datatype"]
    time_offset.id = netCDF_info["variables"]["time_offset"]["id"]
    time_offset.optional = netCDF_info["variables"]["time_offset"]["optional"]

    # Variable: time
    time = JOSS_CDF.createVariable(
        netCDF_info["variables"]["time"]["name"],
        "f8",
        (netCDF_info["dimensions"]["time"]["symbol"],),
    )
    time[:] = (
        (
            day_data.index
            - datetime(
                day_data.index[0].year,
                day_data.index[0].month,
                day_data.index[0].day,
                0,
                0,
            )
        )
        .map(lambda x: x.total_seconds())
        .to_numpy()
        .astype("float64")
    )

    time.shortname = netCDF_info["variables"]["time"]["shortname"]
    time.description = netCDF_info["variables"]["time"]["description"]
    time.unit = netCDF_info["variables"]["time"]["unit"]
    time.datatype = netCDF_info["variables"]["time"]["datatype"]
    time.id = netCDF_info["variables"]["time"]["id"]
    time.optional = netCDF_info["variables"]["time"]["optional"]

    # ######################## DATA VARIABLES ###########################

    # Variable: mean_diam
    mean_diam = JOSS_CDF.createVariable(
        netCDF_info["variables"]["mean_diam"]["name"],
        "f8",
        (netCDF_info["dimensions"]["drop_class"]["symbol"],),
    )

    mean_diam.shortname = netCDF_info["variables"]["mean_diam"]["shortname"]
    mean_diam.description = netCDF_info["variables"]["mean_diam"]["description"]
    mean_diam.unit = netCDF_info["variables"]["mean_diam"]["unit"]
    mean_diam.datatype = netCDF_info["variables"]["mean_diam"]["datatype"]
    mean_diam.id = netCDF_info["variables"]["mean_diam"]["id"]
    mean_diam.optional = netCDF_info["variables"]["mean_diam"]["optional"]

    mean_diam[:] = variables_info["mean_diam"]

    # Variable: velocity
    velocity = JOSS_CDF.createVariable(
        netCDF_info["variables"]["velocity"]["name"],
        "f8",
        (netCDF_info["dimensions"]["drop_class"]["symbol"],),
    )

    velocity.shortname = netCDF_info["variables"]["velocity"]["shortname"]
    velocity.description = netCDF_info["variables"]["velocity"]["description"]
    velocity.unit = netCDF_info["variables"]["velocity"]["unit"]
    velocity.datatype = netCDF_info["variables"]["velocity"]["datatype"]
    velocity.id = netCDF_info["variables"]["velocity"]["id"]
    velocity.optional = netCDF_info["variables"]["velocity"]["optional"]

    velocity[:] = variables_info["velocity"]

    # Variable: diam_interval
    diam_interval = JOSS_CDF.createVariable(
        netCDF_info["variables"]["diam_interval"]["name"],
        "f8",
        (netCDF_info["dimensions"]["drop_class"]["symbol"],),
    )

    diam_interval.shortname = netCDF_info["variables"]["diam_interval"]["shortname"]
    diam_interval.description = netCDF_info["variables"]["diam_interval"]["description"]
    diam_interval.unit = netCDF_info["variables"]["diam_interval"]["unit"]
    diam_interval.datatype = netCDF_info["variables"]["diam_interval"]["datatype"]
    diam_interval.id = netCDF_info["variables"]["diam_interval"]["id"]
    diam_interval.optional = netCDF_info["variables"]["diam_interval"]["optional"]

    diam_interval[:] = variables_info["delta_diam"]

    # Variable: n
    n = JOSS_CDF.createVariable(
        netCDF_info["variables"]["n"]["name"],
        "f8",
        (
            netCDF_info["dimensions"]["time"]["symbol"],
            netCDF_info["dimensions"]["drop_class"]["symbol"],
        ),
    )

    n.shortname = netCDF_info["variables"]["n"]["shortname"]
    n.description = netCDF_info["variables"]["n"]["description"]
    n.unit = netCDF_info["variables"]["n"]["unit"]
    n.datatype = netCDF_info["variables"]["n"]["datatype"]
    n.id = netCDF_info["variables"]["n"]["id"]
    n.optional = netCDF_info["variables"]["n"]["optional"]

    n[:, :] = day_data[columns[4:24]].to_numpy().astype("float64")

    # Variable: d_max
    d_max = JOSS_CDF.createVariable(
        netCDF_info["variables"]["d_max"]["name"],
        "f8",
        (netCDF_info["dimensions"]["time"]["symbol"],),
    )

    d_max.shortname = netCDF_info["variables"]["d_max"]["shortname"]
    d_max.description = netCDF_info["variables"]["d_max"]["description"]
    d_max.unit = netCDF_info["variables"]["d_max"]["unit"]
    d_max.datatype = netCDF_info["variables"]["d_max"]["datatype"]
    d_max.id = netCDF_info["variables"]["d_max"]["id"]
    d_max.optional = netCDF_info["variables"]["d_max"]["optional"]

    d_max[:] = np.array(get_d_max(day_data[variables_info["drop_size"]])).astype(
        "float64"
    )

    # Variable: n_d
    n_d = JOSS_CDF.createVariable(
        netCDF_info["variables"]["n_d"]["name"],
        "f8",
        (
            netCDF_info["dimensions"]["time"]["symbol"],
            netCDF_info["dimensions"]["drop_class"]["symbol"],
        ),
    )

    n_d.shortname = netCDF_info["variables"]["n_d"]["shortname"]
    n_d.description = netCDF_info["variables"]["n_d"]["description"]
    n_d.unit = netCDF_info["variables"]["n_d"]["unit"]
    n_d.datatype = netCDF_info["variables"]["n_d"]["datatype"]
    n_d.id = netCDF_info["variables"]["n_d"]["id"]
    n_d.optional = netCDF_info["variables"]["n_d"]["optional"]

    n_d[:, :] = np.array(
        get_n_d(
            day_data[variables_info["drop_size"]],
            variables_info["drop_size"],
            variables_info["delta_diam"],
            variables_info["velocity"],
            variables_info["integration_time"],
        )
    ).astype("float64")

    # Variable: ri
    ri = JOSS_CDF.createVariable(
        netCDF_info["variables"]["ri"]["name"],
        "f8",
        (netCDF_info["dimensions"]["time"]["symbol"],),
    )

    ri.shortname = netCDF_info["variables"]["ri"]["shortname"]
    ri.description = netCDF_info["variables"]["ri"]["description"]
    ri.unit = netCDF_info["variables"]["ri"]["unit"]
    ri.datatype = netCDF_info["variables"]["ri"]["datatype"]
    ri.id = netCDF_info["variables"]["ri"]["id"]
    ri.optional = netCDF_info["variables"]["ri"]["optional"]

    ri[:] = np.array(
        get_ri(
            day_data[variables_info["drop_size"]],
            variables_info["drop_size"],
            variables_info["mean_diam"],
            variables_info["velocity"],
            variables_info["integration_time"],
        )
    ).astype("float64")

    # Variable: zdb
    zdb = JOSS_CDF.createVariable(
        netCDF_info["variables"]["zdb"]["name"],
        "f8",
        (netCDF_info["dimensions"]["time"]["symbol"],),
    )

    zdb.shortname = netCDF_info["variables"]["zdb"]["shortname"]
    zdb.description = netCDF_info["variables"]["zdb"]["description"]
    zdb.unit = netCDF_info["variables"]["zdb"]["unit"]
    zdb.datatype = netCDF_info["variables"]["zdb"]["datatype"]
    zdb.id = netCDF_info["variables"]["zdb"]["id"]
    zdb.optional = netCDF_info["variables"]["zdb"]["optional"]

    zdb[:] = np.array(
        get_zdb(
            get_z(
                day_data[variables_info["drop_size"]],
                variables_info["drop_size"],
                variables_info["mean_diam"],
                variables_info["velocity"],
                variables_info["integration_time"],
            )
        )
    ).astype("float64")

    # Variable: lwc
    lwc = JOSS_CDF.createVariable(
        netCDF_info["variables"]["lwc"]["name"],
        "f8",
        (netCDF_info["dimensions"]["time"]["symbol"],),
    )

    lwc.shortname = netCDF_info["variables"]["lwc"]["shortname"]
    lwc.description = netCDF_info["variables"]["lwc"]["description"]
    lwc.unit = netCDF_info["variables"]["lwc"]["unit"]
    lwc.datatype = netCDF_info["variables"]["lwc"]["datatype"]
    lwc.id = netCDF_info["variables"]["lwc"]["id"]
    lwc.optional = netCDF_info["variables"]["lwc"]["optional"]

    lwc[:] = np.array(
        get_lwc(
            day_data[variables_info["drop_size"]],
            variables_info["drop_size"],
            variables_info["mean_diam"],
            variables_info["velocity"],
            variables_info["integration_time"],
        )
    ).astype("float64")

    # Variable: ef
    ef = JOSS_CDF.createVariable(
        netCDF_info["variables"]["ef"]["name"],
        "f8",
        (netCDF_info["dimensions"]["time"]["symbol"],),
    )

    ef.shortname = netCDF_info["variables"]["ef"]["shortname"]
    ef.description = netCDF_info["variables"]["ef"]["description"]
    ef.unit = netCDF_info["variables"]["ef"]["unit"]
    ef.datatype = netCDF_info["variables"]["ef"]["datatype"]
    ef.id = netCDF_info["variables"]["ef"]["id"]
    ef.optional = netCDF_info["variables"]["ef"]["optional"]

    ef[:] = np.array(
        get_ef(
            get_ek(
                day_data[variables_info["drop_size"]],
                variables_info["drop_size"],
                variables_info["mean_diam"],
                variables_info["velocity"],
            ),
            variables_info["integration_time"],
        )
    ).astype("float64")

    # Variable: slope
    slope = JOSS_CDF.createVariable(
        netCDF_info["variables"]["slope"]["name"],
        "f8",
        (netCDF_info["dimensions"]["time"]["symbol"],),
    )

    slope.shortname = netCDF_info["variables"]["slope"]["shortname"]
    slope.description = netCDF_info["variables"]["slope"]["description"]
    slope.unit = netCDF_info["variables"]["slope"]["unit"]
    slope.datatype = netCDF_info["variables"]["slope"]["datatype"]
    slope.id = netCDF_info["variables"]["slope"]["id"]
    slope.optional = netCDF_info["variables"]["slope"]["optional"]

    slope[:] = np.array(
        get_slope(
            get_lwc(
                day_data[variables_info["drop_size"]],
                variables_info["drop_size"],
                variables_info["mean_diam"],
                variables_info["velocity"],
                variables_info["integration_time"],
            ),
            get_z(
                day_data[variables_info["drop_size"]],
                variables_info["drop_size"],
                variables_info["mean_diam"],
                variables_info["velocity"],
                variables_info["integration_time"],
            ),
        )
    ).astype("float64")

    # Variable: slope
    n_0 = JOSS_CDF.createVariable(
        netCDF_info["variables"]["n_0"]["name"],
        "f8",
        (netCDF_info["dimensions"]["time"]["symbol"],),
    )

    n_0.shortname = netCDF_info["variables"]["n_0"]["shortname"]
    n_0.description = netCDF_info["variables"]["n_0"]["description"]
    n_0.unit = netCDF_info["variables"]["n_0"]["unit"]
    n_0.datatype = netCDF_info["variables"]["n_0"]["datatype"]
    n_0.id = netCDF_info["variables"]["n_0"]["id"]
    n_0.optional = netCDF_info["variables"]["n_0"]["optional"]

    n_0[:] = np.array(
        get_n_0(
            get_lwc(
                day_data[variables_info["drop_size"]],
                variables_info["drop_size"],
                variables_info["mean_diam"],
                variables_info["velocity"],
                variables_info["integration_time"],
            ),
            get_z(
                day_data[variables_info["drop_size"]],
                variables_info["drop_size"],
                variables_info["mean_diam"],
                variables_info["velocity"],
                variables_info["integration_time"],
            ),
        )
    ).astype("float64")

    print("netCDF created")

    JOSS_CDF.close()
