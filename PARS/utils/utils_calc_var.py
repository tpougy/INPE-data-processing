from math import pi

import numpy as np

# Effetive parsivel area
def calc_seff(drop_class):
    return [(180 * (30 - (d / 2))) * (pow(10, -6)) for d in drop_class]


# number of particles per drop class
def calc_n(vpd):
    return [np.sum(np.asarray(vpd)[:, col]) for col in range(len(vpd[0]))]


# concentration of particles per unit of volume passing by the effective surface area of the sensor
def calc_npv(n, seff, delta_diam, vel_diam, integration_time):
    return [
        (n_dc / (seff_dc * delta_diam_dc)) * integration_time / vel_diam_dc
        for n_dc, seff_dc, delta_diam_dc, vel_diam_dc in zip(
            n, seff, delta_diam, vel_diam
        )
    ]


def calc_aux_var(data, drop_class, vel_diam, delta_diam):
    n = []
    seff = []
    for _, row in data.iterrows():

        n.append(calc_n(row["vpd"]))

        seff.append(calc_seff(drop_class))

    return [
        calc_npv(n_i, seff_i, delta_diam, vel_diam, row["interval_sample"])
        for (_, row), n_i, seff_i in zip(data.iterrows(), n, seff)
    ]


# npv_dc is the concentration of particles per unit of volume per drop class
def calc_ri(npv, drop_class, vel_diam, delta_diam):
    c = 6 * pi * pow(10, -6)

    rain_rate = []

    for npv_i in npv:

        r = c * sum(
            npv_dc * v_dc * pow(d, 3) * dd_dc
            for npv_dc, d, v_dc, dd_dc in zip(npv_i, drop_class, vel_diam, delta_diam)
        )

        rain_rate.append(r)

    return rain_rate


def calc_liq_water(npv, drop_class, vel_diam, delta_diam):
    c = 6 * pi * pow(10, -6)

    liq_water = []
    for npv_i in npv:

        r = c * sum(
            npv_dc * pow(d, 3) * dd_dc
            for npv_dc, d, dd_dc in zip(npv_i, drop_class, delta_diam)
        )

        liq_water.append(r)

    return liq_water


def calc_z(npv, drop_class, vel_diam, delta_diam):
    c = 6 * pi * pow(10, -6)

    zdb = []
    for npv_i in npv:

        r = sum(
            npv_dc * pow(d, 6) * dd_dc
            for npv_dc, d, dd_dc in zip(npv_i, drop_class, delta_diam)
        )

        zdb.append(r)

    return zdb
