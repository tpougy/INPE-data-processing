import os

import numpy as np
from netCDF4 import Dataset

from .utils_encode import string2ascii_array


def generate_netCDF(
    cdf_filename,
    day_data,
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

    PARS_CDF = Dataset(path_output_data.joinpath(cdf_filename), "w", format="NETCDF4")

    # ######################## DIMENSIONS ##########################

    drop_class = PARS_CDF.createDimension(
        netCDF_info["dimensions"]["drop_class"]["symbol"], 20
    )

    time = PARS_CDF.createDimension(
        netCDF_info["dimensions"]["time"]["symbol"], day_data.shape[0]
    )

    str_dim = PARS_CDF.createDimension("str_dim", 255)

    # ######################## GLOBAL VARIABLES ###########################

    # Variable: data_description
    data_description = PARS_CDF.createVariable(
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

    # Variable: site_id
    site_id = PARS_CDF.createVariable(
        netCDF_info["global"]["site_identifier"]["name"], "u8"
    )
    site_id[:] = np.int64(netCDF_info["global"]["site_identifier"]["value"])

    site_id.shortname = netCDF_info["global"]["site_identifier"]["shortname"]
    site_id.description = netCDF_info["global"]["site_identifier"]["description"]
    site_id.unit = netCDF_info["global"]["site_identifier"]["unit"]
    site_id.datatype = netCDF_info["global"]["site_identifier"]["datatype"]
    site_id.id = netCDF_info["global"]["site_identifier"]["id"]
    site_id.optional = netCDF_info["global"]["site_identifier"]["optional"]

    # Variable: platform_id
    platform_id = PARS_CDF.createVariable(
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

    # Variable: facility_id
    facility_id = PARS_CDF.createVariable(
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

    # Variable: data_level
    data_level = PARS_CDF.createVariable(
        netCDF_info["global"]["data_level"]["name"], "u8"
    )
    data_level[:] = np.int64(netCDF_info["global"]["data_level"]["value"])

    data_level.shortname = netCDF_info["global"]["data_level"]["shortname"]
    data_level.description = netCDF_info["global"]["data_level"]["description"]
    data_level.unit = netCDF_info["global"]["data_level"]["unit"]
    data_level.datatype = netCDF_info["global"]["data_level"]["datatype"]
    data_level.id = netCDF_info["global"]["data_level"]["id"]
    data_level.optional = netCDF_info["global"]["data_level"]["optional"]

    # Variable: location
    location = PARS_CDF.createVariable(netCDF_info["global"]["location"]["name"], "u8")
    location[:] = np.int64(netCDF_info["global"]["location"]["value"])

    location.shortname = netCDF_info["global"]["location"]["shortname"]
    location.description = netCDF_info["global"]["location"]["description"]
    location.unit = netCDF_info["global"]["location"]["unit"]
    location.datatype = netCDF_info["global"]["location"]["datatype"]
    location.id = netCDF_info["global"]["location"]["id"]
    location.optional = netCDF_info["global"]["location"]["optional"]

    # Variable: datastream
    variable: datastream
    datastream = PARS_CDF.createVariable(
        netCDF_info["global"]["datastream"]["name"], "u8", ("str_dim",)
    )
    datastream[:] = string2ascii_array(netCDF_info["global"]["datastream"]["value"])

    datastream.shortname = netCDF_info["global"]["datastream"]["shortname"]
    datastream.description = netCDF_info["global"]["datastream"]["description"]
    datastream.unit = netCDF_info["global"]["datastream"]["unit"]
    datastream.datatype = netCDF_info["global"]["datastream"]["datatype"]
    datastream.id = netCDF_info["global"]["datastream"]["id"]
    datastream.optional = netCDF_info["global"]["datastream"]["optional"]

    # Variable: samp_interval
    samp_interval = PARS_CDF.createVariable(
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

    # Variable: avar_interval
    avar_interval = PARS_CDF.createVariable(
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

    # Variable: serial_number
    serial_number = PARS_CDF.createVariable(
        netCDF_info["global"]["serial_number"]["name"], "u8"
    )
    serial_number[:] = np.int64(netCDF_info["global"]["serial_number"]["value"])

    serial_number.shortname = netCDF_info["global"]["serial_number"]["shortname"]
    serial_number.description = netCDF_info["global"]["serial_number"]["description"]
    serial_number.unit = netCDF_info["global"]["serial_number"]["unit"]
    serial_number.datatype = netCDF_info["global"]["serial_number"]["datatype"]
    serial_number.id = netCDF_info["global"]["serial_number"]["id"]
    serial_number.optional = netCDF_info["global"]["serial_number"]["optional"]

    # Variable: calibration_date
    calibration_date = PARS_CDF.createVariable(
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

    # Variable: lat
    lat = PARS_CDF.createVariable(netCDF_info["global"]["lat"]["name"], "u8")
    lat[:] = np.float64(netCDF_info["global"]["lat"]["value"])

    lat.shortname = netCDF_info["global"]["lat"]["shortname"]
    lat.description = netCDF_info["global"]["lat"]["description"]
    lat.unit = netCDF_info["global"]["lat"]["unit"]
    lat.datatype = netCDF_info["global"]["lat"]["datatype"]
    lat.id = netCDF_info["global"]["lat"]["id"]
    lat.optional = netCDF_info["global"]["lat"]["optional"]

    # Variable: lon
    lon = PARS_CDF.createVariable(netCDF_info["global"]["lon"]["name"], "u8")
    lon[:] = np.float64(netCDF_info["global"]["lon"]["value"])

    lon.shortname = netCDF_info["global"]["lon"]["shortname"]
    lon.description = netCDF_info["global"]["lon"]["description"]
    lon.unit = netCDF_info["global"]["lon"]["unit"]
    lon.datatype = netCDF_info["global"]["lon"]["datatype"]
    lon.id = netCDF_info["global"]["lon"]["id"]
    lon.optional = netCDF_info["global"]["lon"]["optional"]

    # Variable: alt
    alt = PARS_CDF.createVariable(netCDF_info["global"]["alt"]["name"], "u8")
    alt[:] = np.float64(netCDF_info["global"]["alt"]["value"])

    alt.shortname = netCDF_info["global"]["alt"]["shortname"]
    alt.description = netCDF_info["global"]["alt"]["description"]
    alt.unit = netCDF_info["global"]["alt"]["unit"]
    alt.datatype = netCDF_info["global"]["alt"]["datatype"]
    alt.id = netCDF_info["global"]["alt"]["id"]
    alt.optional = netCDF_info["global"]["alt"]["optional"]

    # ######################## TIME VARIABLES ###########################

    # Variable: base_time (u8 is 32-bit unsigned integer)
    base_time = PARS_CDF.createVariable(
        netCDF_info["variables"]["base_time"]["name"],
        "u8",
    )
    base_time[:] = np.int64(day_data.index[0].timestamp())

    base_time.shortname = netCDF_info["variables"]["base_time"]["shortname"]
    base_time.description = netCDF_info["variables"]["base_time"]["description"]
    base_time.unit = netCDF_info["variables"]["base_time"]["unit"]
    base_time.datatype = netCDF_info["variables"]["base_time"]["datatype"]
    base_time.id = netCDF_info["variables"]["base_time"]["id"]
    base_time.optional = netCDF_info["variables"]["base_time"]["optional"]

    # Variable: time_offset (f8 is 32-bit unsigned float)
    time_offset = PARS_CDF.createVariable(
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
    time = PARS_CDF.createVariable(
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

    # @@ Variable: mean_diam
    mean_diam = PARS_CDF.createVariable(
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

    # @@ Variable: velocity
    velocity = PARS_CDF.createVariable(
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

    # @@ Variable: diam_interval
    diam_interval = PARS_CDF.createVariable(
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

    # @@ Variable: ri
    ri = PARS_CDF.createVariable(
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

    # @@ Variable: zdb
    zdb = PARS_CDF.createVariable(
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

    # @@ Variable: lwc
    lwc = PARS_CDF.createVariable(
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

    # @@ Variable: ef
    ef = PARS_CDF.createVariable(
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

    print("netCDF created")

    PARS_CDF.close()
