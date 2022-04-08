from math import pi

import numpy as np

# Effetive parsivel area
def calc_seff(mean_diam):
    return [(180 * (30 - (d / 2))) * (pow(10, -6)) for d in mean_diam]


# number of particles per drop class
def calc_n(vpd):
    return [np.sum(np.asarray(vpd)[:, col]) for col in range(len(vpd[0]))]


# concentration of particles per unit of volume passing by the effective surface area of the sensor
def calc_npv(n, seff, delta_diam, integration_time, vel_diam):
    return [
        (n_dc / (seff_dc * delta_diam_dc)) * integration_time / vel_diam_dc
        for n_dc, seff_dc, delta_diam_dc, vel_diam_dc in zip(
            n, seff, delta_diam, vel_diam
        )
    ]


# npv_dc is the concentration of particles per unit of volume per drop class
def calc_ri(data, mean_diam, vel_diam, delta_diam):
    c = 6 * pi * pow(10, -6)

    ri = []
    for _, row in data.iterrows():

        n = calc_n(row["vpd"])

        seff = calc_seff(mean_diam)

        npv = calc_npv(n, seff, delta_diam, row["sample_interval"], vel_diam)

        r = c * sum(
            npv_dc * v_dc * pow(d, 3) * dd_dc
            for npv_dc, d, v_dc, dd_dc in zip(npv, mean_diam, vel_diam, delta_diam)
        )

        ri.append(r)

    return ri


def calc_lwc(data, mean_diam, vel_diam, delta_diam):
    c = 6 * pi * pow(10, -6)

    lwc = []
    for _, row in data.iterrows():

        n = calc_n(row["vpd"])

        seff = calc_seff(mean_diam)

        npv = calc_npv(n, seff, delta_diam, row["sample_interval"], vel_diam)

        r = c * sum(
            npv_dc * pow(d, 3) * dd_dc
            for npv_dc, d, dd_dc in zip(npv, mean_diam, delta_diam)
        )

        lwc.append(r)

    return lwc


def calc_z(data, mean_diam, vel_diam, delta_diam):
    c = 6 * pi * pow(10, -6)

    z = []
    for _, row in data.iterrows():

        n = calc_n(row["vpd"])

        seff = calc_seff(mean_diam)

        npv = calc_npv(n, seff, delta_diam, row["sample_interval"], vel_diam)

        r = sum(
            npv_dc * pow(d, 6) * dd_dc
            for npv_dc, d, dd_dc in zip(npv, mean_diam, delta_diam)
        )

        z.append(r)

    return z
