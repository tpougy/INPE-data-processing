# Seff=(180.*(30. -(class_ps(col)/2.)))*(10^(-6.)) ;Effetive parsivel area
def get_seff(mean_diam):
    return [(180 * (30 - (d / 2))) * (pow(10, -6)) for d in mean_diam]


def get_ni(vpd):
    return [np.sum(np.asarray(vpd)[:, col]) for col in vpd]


# O que é dT? procurar em disdrometer.pro
def get_ndrop(seff, ni, delta_diam, dt, vel_diam):
    pass
