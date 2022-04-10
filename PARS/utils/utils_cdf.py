import os

import numpy as np
from netCDF4 import Dataset
from datetime import datetime

from .utils_encode import string2ascii_array
from .utils_calc_var import *


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

    # value defined as 32 in the json file
    drop_class = PARS_CDF.createDimension(
        netCDF_info["dimensions"]["drop_class"]["symbol"],
        netCDF_info["dimensions"]["drop_class"]["value"],
    )

    time = PARS_CDF.createDimension(
        netCDF_info["dimensions"]["time"]["symbol"], day_data.shape[0]
    )

    # value defined as 255 in the json file
    str_dim = PARS_CDF.createDimension(
        netCDF_info["dimensions"]["str_dim"]["symbol"],
        netCDF_info["dimensions"]["str_dim"]["value"],
    )

    # ######################## GLOBAL VARIABLES ###########################

    # Variable: description
    description = PARS_CDF.createVariable(
        netCDF_info["global"]["description"]["name"], "u8", ("str_dim",)
    )
    description[:] = string2ascii_array(netCDF_info["global"]["description"]["value"])

    description.shortname = netCDF_info["global"]["description"]["shortname"]
    description.description = netCDF_info["global"]["description"]["description"]
    description.unit = netCDF_info["global"]["description"]["unit"]
    description.datatype = netCDF_info["global"]["description"]["datatype"]
    description.id = netCDF_info["global"]["description"]["id"]
    description.optional = netCDF_info["global"]["description"]["optional"]

    # Variable: site_id
    site_id = PARS_CDF.createVariable(netCDF_info["global"]["site_id"]["name"], "u8")
    site_id[:] = np.int64(netCDF_info["global"]["site_id"]["value"])

    site_id.shortname = netCDF_info["global"]["site_id"]["shortname"]
    site_id.description = netCDF_info["global"]["site_id"]["description"]
    site_id.unit = netCDF_info["global"]["site_id"]["unit"]
    site_id.datatype = netCDF_info["global"]["site_id"]["datatype"]
    site_id.id = netCDF_info["global"]["site_id"]["id"]
    site_id.optional = netCDF_info["global"]["site_id"]["optional"]

    # Variable: platform_id
    platform_id = PARS_CDF.createVariable(
        netCDF_info["global"]["platform_id"]["name"], "u8"
    )
    platform_id[:] = np.int64(netCDF_info["global"]["platform_id"]["value"])

    platform_id.shortname = netCDF_info["global"]["platform_id"]["shortname"]
    platform_id.description = netCDF_info["global"]["platform_id"]["description"]
    platform_id.unit = netCDF_info["global"]["platform_id"]["unit"]
    platform_id.datatype = netCDF_info["global"]["platform_id"]["datatype"]
    platform_id.id = netCDF_info["global"]["platform_id"]["id"]
    platform_id.optional = netCDF_info["global"]["platform_id"]["optional"]

    # Variable: facility_id
    facility_id = PARS_CDF.createVariable(
        netCDF_info["global"]["facility_id"]["name"], "u8"
    )
    facility_id[:] = np.int64(netCDF_info["global"]["facility_id"]["value"])

    facility_id.shortname = netCDF_info["global"]["facility_id"]["shortname"]
    facility_id.description = netCDF_info["global"]["facility_id"]["description"]
    facility_id.unit = netCDF_info["global"]["facility_id"]["unit"]
    facility_id.datatype = netCDF_info["global"]["facility_id"]["datatype"]
    facility_id.id = netCDF_info["global"]["facility_id"]["id"]
    facility_id.optional = netCDF_info["global"]["facility_id"]["optional"]

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

    # Variable: location_description
    location_description = PARS_CDF.createVariable(
        netCDF_info["global"]["location_description"]["name"], "u8"
    )
    location_description[:] = np.int64(
        netCDF_info["global"]["location_description"]["value"]
    )

    location_description.shortname = netCDF_info["global"]["location_description"][
        "shortname"
    ]
    location_description.description = netCDF_info["global"]["location_description"][
        "description"
    ]
    location_description.unit = netCDF_info["global"]["location_description"]["unit"]
    location_description.datatype = netCDF_info["global"]["location_description"][
        "datatype"
    ]
    location_description.id = netCDF_info["global"]["location_description"]["id"]
    location_description.optional = netCDF_info["global"]["location_description"][
        "optional"
    ]

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

    # Variable: calib_date
    calib_date = PARS_CDF.createVariable(
        netCDF_info["global"]["calib_date"]["name"], "u8"
    )
    calib_date[:] = np.datetime64(netCDF_info["global"]["calib_date"]["value"])

    calib_date.shortname = netCDF_info["global"]["calib_date"]["shortname"]
    calib_date.description = netCDF_info["global"]["calib_date"]["description"]
    calib_date.unit = netCDF_info["global"]["calib_date"]["unit"]
    calib_date.datatype = netCDF_info["global"]["calib_date"]["datatype"]
    calib_date.id = netCDF_info["global"]["calib_date"]["id"]
    calib_date.optional = netCDF_info["global"]["calib_date"]["optional"]

    # Variable: lat
    lat = PARS_CDF.createVariable(netCDF_info["global"]["lat"]["name"], "f8")
    lat[:] = np.float64(netCDF_info["global"]["lat"]["value"])

    lat.shortname = netCDF_info["global"]["lat"]["shortname"]
    lat.description = netCDF_info["global"]["lat"]["description"]
    lat.unit = netCDF_info["global"]["lat"]["unit"]
    lat.datatype = netCDF_info["global"]["lat"]["datatype"]
    lat.id = netCDF_info["global"]["lat"]["id"]
    lat.optional = netCDF_info["global"]["lat"]["optional"]

    # Variable: lon
    lon = PARS_CDF.createVariable(netCDF_info["global"]["lon"]["name"], "f8")
    lon[:] = np.float64(netCDF_info["global"]["lon"]["value"])

    lon.shortname = netCDF_info["global"]["lon"]["shortname"]
    lon.description = netCDF_info["global"]["lon"]["description"]
    lon.unit = netCDF_info["global"]["lon"]["unit"]
    lon.datatype = netCDF_info["global"]["lon"]["datatype"]
    lon.id = netCDF_info["global"]["lon"]["id"]
    lon.optional = netCDF_info["global"]["lon"]["optional"]

    # Variable: alt
    alt = PARS_CDF.createVariable(netCDF_info["global"]["alt"]["name"], "f8")
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

    # ################## PARSIVEL PARAMETERS VARIABLES ###########################

    # Variable: drop_class
    drop_class = PARS_CDF.createVariable(
        netCDF_info["variables"]["drop_class"]["name"],
        "f8",
        (netCDF_info["dimensions"]["drop_class"]["symbol"],),
    )

    drop_class.shortname = netCDF_info["variables"]["drop_class"]["shortname"]
    drop_class.description = netCDF_info["variables"]["drop_class"]["description"]
    drop_class.unit = netCDF_info["variables"]["drop_class"]["unit"]
    drop_class.datatype = netCDF_info["variables"]["drop_class"]["datatype"]
    drop_class.id = netCDF_info["variables"]["drop_class"]["id"]
    drop_class.optional = netCDF_info["variables"]["drop_class"]["optional"]

    drop_class[:] = variables_info["drop_class_param"]["drop_class"]

    # Variable: fall_vell
    fall_vell = PARS_CDF.createVariable(
        netCDF_info["variables"]["fall_vell"]["name"],
        "f8",
        (netCDF_info["dimensions"]["drop_class"]["symbol"],),
    )

    fall_vell.shortname = netCDF_info["variables"]["fall_vell"]["shortname"]
    fall_vell.description = netCDF_info["variables"]["fall_vell"]["description"]
    fall_vell.unit = netCDF_info["variables"]["fall_vell"]["unit"]
    fall_vell.datatype = netCDF_info["variables"]["fall_vell"]["datatype"]
    fall_vell.id = netCDF_info["variables"]["fall_vell"]["id"]
    fall_vell.optional = netCDF_info["variables"]["fall_vell"]["optional"]

    fall_vell[:] = variables_info["drop_class_param"]["vel_diam"]

    # Variable: delta_diam
    delta_diam = PARS_CDF.createVariable(
        netCDF_info["variables"]["delta_diam"]["name"],
        "f8",
        (netCDF_info["dimensions"]["drop_class"]["symbol"],),
    )

    delta_diam.shortname = netCDF_info["variables"]["delta_diam"]["shortname"]
    delta_diam.description = netCDF_info["variables"]["delta_diam"]["description"]
    delta_diam.unit = netCDF_info["variables"]["delta_diam"]["unit"]
    delta_diam.datatype = netCDF_info["variables"]["delta_diam"]["datatype"]
    delta_diam.id = netCDF_info["variables"]["delta_diam"]["id"]
    delta_diam.optional = netCDF_info["variables"]["delta_diam"]["optional"]

    delta_diam[:] = variables_info["drop_class_param"]["delta_diam"]

    # ############### DATA VARIABLES ###################

    npv = calc_aux_var(
        day_data[["interval_sample", "vpd"]],
        variables_info["drop_class_param"]["drop_class"],
        variables_info["drop_class_param"]["vel_diam"],
        variables_info["drop_class_param"]["delta_diam"],
    )

    # Variable: rain_rate
    rain_rate = PARS_CDF.createVariable(
        netCDF_info["variables"]["rain_rate"]["name"],
        "f8",
        (netCDF_info["dimensions"]["time"]["symbol"],),
    )

    rain_rate.shortname = netCDF_info["variables"]["rain_rate"]["shortname"]
    rain_rate.description = netCDF_info["variables"]["rain_rate"]["description"]
    rain_rate.unit = netCDF_info["variables"]["rain_rate"]["unit"]
    rain_rate.datatype = netCDF_info["variables"]["rain_rate"]["datatype"]
    rain_rate.id = netCDF_info["variables"]["rain_rate"]["id"]
    rain_rate.optional = netCDF_info["variables"]["rain_rate"]["optional"]

    rain_rate[:] = np.array(
        calc_ri(
            npv,
            variables_info["drop_class_param"]["drop_class"],
            variables_info["drop_class_param"]["vel_diam"],
            variables_info["drop_class_param"]["delta_diam"],
        )
    ).astype("float64")

    # Variable: zdb
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
        calc_z(
            npv,
            variables_info["drop_class_param"]["drop_class"],
            variables_info["drop_class_param"]["vel_diam"],
            variables_info["drop_class_param"]["delta_diam"],
        )
    ).astype("float64")

    # Variable: liq_water
    liq_water = PARS_CDF.createVariable(
        netCDF_info["variables"]["liq_water"]["name"],
        "f8",
        (netCDF_info["dimensions"]["time"]["symbol"],),
    )

    liq_water.shortname = netCDF_info["variables"]["liq_water"]["shortname"]
    liq_water.description = netCDF_info["variables"]["liq_water"]["description"]
    liq_water.unit = netCDF_info["variables"]["liq_water"]["unit"]
    liq_water.datatype = netCDF_info["variables"]["liq_water"]["datatype"]
    liq_water.id = netCDF_info["variables"]["liq_water"]["id"]
    liq_water.optional = netCDF_info["variables"]["liq_water"]["optional"]

    liq_water[:] = np.array(
        calc_liq_water(
            npv,
            variables_info["drop_class_param"]["drop_class"],
            variables_info["drop_class_param"]["vel_diam"],
            variables_info["drop_class_param"]["delta_diam"],
        )
    ).astype("float64")

    # Variable: err_code
    err_code = PARS_CDF.createVariable(
        netCDF_info["variables"]["err_code"]["name"],
        "f8",
        (netCDF_info["dimensions"]["time"]["symbol"],),
    )

    err_code.shortname = netCDF_info["variables"]["err_code"]["shortname"]
    err_code.description = netCDF_info["variables"]["err_code"]["description"]
    err_code.unit = netCDF_info["variables"]["err_code"]["unit"]
    err_code.datatype = netCDF_info["variables"]["err_code"]["datatype"]
    err_code.id = netCDF_info["variables"]["err_code"]["id"]
    err_code.optional = netCDF_info["variables"]["err_code"]["optional"]

    err_code[:] = day_data["err_code"].to_numpy().astype("uint64")

    # @@ Variable: raw_spectrum

    raw_spectrum = PARS_CDF.createVariable(
        netCDF_info["variables"]["raw_spectrum"]["name"],
        "f8",
        (
            netCDF_info["dimensions"]["drop_class"]["symbol"],
            netCDF_info["dimensions"]["drop_class"]["symbol"],
            netCDF_info["dimensions"]["time"]["symbol"],
        ),
    )

    raw_spectrum.shortname = netCDF_info["variables"]["raw_spectrum"]["shortname"]
    raw_spectrum.description = netCDF_info["variables"]["raw_spectrum"]["description"]
    raw_spectrum.unit = netCDF_info["variables"]["raw_spectrum"]["unit"]
    raw_spectrum.datatype = netCDF_info["variables"]["raw_spectrum"]["datatype"]
    raw_spectrum.id = netCDF_info["variables"]["raw_spectrum"]["id"]
    raw_spectrum.optional = netCDF_info["variables"]["raw_spectrum"]["optional"]

    raw_spectrum[:] = np.dstack(
        [np.array(reg) for reg in day_data["vpd"].values]
    ).astype("float64")

    PARS_CDF.close()
