# Utilities para o script de processamento de dados
import numpy as np
import pandas as pd
import csv
from datetime import datetime
import os
from matplotlib.pyplot import subplots
import matplotlib.pyplot as plt
import matplotlib
import time
import math
from netCDF4 import Dataset
from netCDF4 import num2date


def Joss_GenerateCDF(data, writeAddress):
    # Abertura de dados originais

    # Inicio da escrita
    file_date = str(data["YYYY-MM-DD"][0])
    file_date = file_date.replace("-", "")
    file_time = str(data["hh:mm:ss"][0])
    file_time = file_time.replace(":", "")

    mean_diam = [
        0.359,
        0.455,
        0.551,
        0.656,
        0.771,
        0.913,
        1.116,
        1.331,
        1.506,
        1.665,
        1.912,
        2.259,
        2.584,
        2.869,
        3.198,
        3.544,
        3.916,
        4.350,
        4.859,
        5.373,
    ]

    velocity = [
        1.435,
        1.862,
        2.267,
        2.692,
        3.154,
        3.717,
        4.382,
        4.986,
        5.423,
        5.793,
        6.315,
        7.009,
        7.546,
        7.903,
        8.258,
        8.556,
        8.784,
        8.965,
        9.076,
        9.137,
    ]

    diam = [
        0.092,
        0.100,
        0.091,
        0.119,
        0.112,
        0.172,
        0.233,
        0.197,
        0.153,
        0.166,
        0.329,
        0.364,
        0.286,
        0.284,
        0.374,
        0.319,
        0.423,
        0.446,
        0.572,
        0.455,
    ]

    liq_water_sum = 0.0
    liq_water_g = []
    for t in range(0, len(data)):
        for i in range(0, 20):
            liq_water_sum += (
                (math.pi / 6)
                * (1 / (0.005 * 60))
                * ((data["n" + str(i + 1)][t] * pow(mean_diam[i], 3)) / (velocity[i]))
            )
        liq_water_g.append(liq_water_sum / 1000)
        liq_water_sum = 0.0

    reflect = 0.0
    zdb_aux = []
    for t in range(0, len(data)):
        for i in range(0, 20):
            reflect += (data["n" + str(i + 1)][t] * pow(mean_diam[i], 6)) / (
                velocity[i]
            )
        if reflect != 0:
            zdb_aux.append(10 * math.log(reflect * (1 / (0.005 * 60)), 10))
        else:
            zdb_aux.append(0.0)
        reflect = 0.0

    KineticSum = 0.0
    KineticEnergy = 0.0
    ef_aux = []
    for t in range(0, len(data)):
        for i in range(0, 20):
            KineticSum += (
                data["n" + str(i + 1)][t] * pow(mean_diam[i], 3) * pow(velocity[i], 2)
            )
        KineticEnergy = (math.pi / 12) * (1 / 0.005) * (1 / pow(10, 6)) * KineticSum
        ef_aux.append((KineticEnergy * 3600) / 60)
        KineticSum = 0.0
        KineticEnergy = 0.0

    slope_aux = []
    for i in range(0, len(data)):
        if zdb_aux[i] != 0:
            slope_aux.append(
                pow(
                    (math.factorial(6) / math.pi)
                    * ((liq_water_g[i] * 1000) / pow(10, zdb_aux[i] / 10)),
                    1 / 3,
                )
            )
        else:
            slope_aux.append(0.0)

    pattern = "%Y-%m-%d %H:%M:%S"
    date_time_diff = [0.0] * len(data)
    offset = [0.0] * len(data)
    date_time = str(data["YYYY-MM-DD"][0]) + str(" ") + str(data["hh:mm:ss"][0])
    utc_time = datetime.strptime(date_time, pattern)
    for i in range(0, len(data)):
        date_offset = str(data["YYYY-MM-DD"][i]) + str(" ") + str(data["hh:mm:ss"][i])
        date_time_diff[i] = datetime.strptime(date_offset, pattern)
        offset[i] = (
            date_time_diff[i]
            - datetime(
                utc_time.year,
                utc_time.month,
                utc_time.day,
                utc_time.hour,
                utc_time.minute,
                utc_time.second,
            )
        ).total_seconds()

    inpeCDF = Dataset(
        writeAddress + "\\attimpactdisdcam.b0." + file_date + "." + file_time + ".nc",
        "w",
        format="NETCDF4",
    )  # Escrita com modelo de nome de arquivo
    inpeCDF.description = (
        "Data collected from an impact disdrometer in the ATTO-Campina site"
    )
    inpeCDF.site_id = "att"
    inpeCDF.platform_id = "jwd"
    inpeCDF.facility_id = "cam"
    inpeCDF.data_level = "b0"
    inpeCDF.location_description = (
        "Amazon Tall Tower Observatory (ATTO), Amazonia, Brazil"
    )
    inpeCDF.datastream = "attimpactdisdcam.bo"
    inpeCDF.sampling_interval = "1 minute"
    inpeCDF.averaging_interval = "N/A"

    # Todo arquivo netCDF contem dimensions e variables (nao usaremos groups aqui)
    # Comecamos definindo as dimensions da mesma forma como o arquivo do ARM
    inpeCDF.createDimension("time", len(data))
    inpeCDF.createDimension("drop_class", 20)

    # Variable: rain_rate
    rain_rate = inpeCDF.createVariable(
        "rain_rate", "f4", ("time",)
    )  # f4 == 32-bit float
    rain_rate.units = "mm/hr"
    rain_rate.long_name = "Rain rate"
    rain_rate.valid_min = 0.0
    rain_rate.missing_value = -99.0
    rain_rate[:] = data["RI [mm/h]"][:]

    # Variable: num_drop
    num_drop = inpeCDF.createVariable("num_drop", "f4", ("time", "drop_class"))
    num_drop.units = "none"
    num_drop.long_name = "Number of drops"
    num_drop.valid_min = 0.0
    num_drop.missing_value = -99.0
    for i in range(0, 20):
        num_drop[:, i] = data["n" + str(i + 1)][:]

    # Variable: base_time / Primeira medição do arquivo / De acordo com ARM
    base_time = inpeCDF.createVariable(
        "base_time", "u4"
    )  # u4 == 32-bit unsigned integer
    base_time.units = "seconds since 1970-1-1 0:00:00 0:00"
    base_time.long_name = "Base time in Epoch"
    date_time = str(data["YYYY-MM-DD"][0]) + str(" ") + str(data["hh:mm:ss"][0])
    pattern = "%Y-%m-%d %H:%M:%S"
    utc_time = datetime.strptime(date_time, pattern)
    epoch_time = int((utc_time - datetime(1970, 1, 1)).total_seconds())
    base_time[:] = epoch_time

    # Variable: time
    time = inpeCDF.createVariable("time", "f8", ("time",))
    time.long_name = "Time offset from midnight"
    time.units = "seconds since " + str(data["YYYY-MM-DD"][0]) + "midnight"
    pattern_diff = "%Y-%m-%d %H:%M:%S"
    date_time_diff = [0.0] * len(data)
    offset = [0.0] * len(data)
    for i in range(0, len(data)):
        date_time = str(data["YYYY-MM-DD"][i]) + str(" ") + str(data["hh:mm:ss"][i])
        date_time_diff[i] = datetime.strptime(date_time, pattern)
        offset[i] = (
            date_time_diff[i]
            - datetime(utc_time.year, utc_time.month, utc_time.day, 0, 0)
        ).total_seconds()
    time[:] = offset[:]

    # Variable: time_offset
    time_offset = inpeCDF.createVariable("time_offset", "f8", ("time",))
    time_offset.long_name = "Time offset from base_time"
    time_offset.units = (
        "seconds since "
        + str(data["YYYY-MM-DD"][0])
        + str(" ")
        + str(data["hh:mm:ss"][0])
    )
    time_offset[:] = offset[:]

    # Variable: mean_diam_drop_class / Dados obtidos do manual do instrumento
    mean_diam_drop_class = inpeCDF.createVariable(
        "mean_diam_drop_class", "f4", ("drop_class",)
    )
    mean_diam_drop_class.units = "mm"
    mean_diam_drop_class.long_name = "Diameter of drop size class"
    mean_diam_drop_class.missing_value = -99.0
    mean_diam_drop_class[:] = mean_diam[:]

    # Variable: fall_vel / Dados obtidos do manual do instrumento
    fall_vel = inpeCDF.createVariable("fall_vel", "f4", ("drop_class",))
    fall_vel.units = "m/s"
    fall_vel.long_name = "Fall velocity"
    fall_vel.missing_value = -99.0
    fall_vel[:] = velocity[:]

    # Variable: delta_diam / Dados obtidos do manual do instrumento
    delta_diam = inpeCDF.createVariable("delta_diam", "f4", ("drop_class",))
    delta_diam.long_name = "Diameter interval between drop size classes"
    delta_diam.units = "mm"
    delta_diam.missing_value = -99.0
    delta_diam[:] = diam[:]

    # Variable: lat
    lat = inpeCDF.createVariable("lat", "f4")
    lat.long_name = "North latitude"
    lat.units = "degree_N"
    lat.valid_min = -90.0
    lat.valid_max = 90.0

    lat[:] = -2.1814
    # Variable: lon
    lon = inpeCDF.createVariable("lon", "f4")
    lon.long_name = "East longitude"
    lon.units = "degree_E"
    lon.valid_min = -180.0
    lon.valid_max = 180.0

    lon[:] = -59.0218
    # Variable: alt
    alt = inpeCDF.createVariable("alt", "f4")
    alt.long_name = "Altitude above mean sea level"
    alt.units = "m"

    alt[:] = 37.0

    # Variable: liq_water / Formulas para encontrar obtidas do manual do instrumento
    liq_water = inpeCDF.createVariable("liq_water", "f4", ("time",))
    liq_water.long_name = "Liquid water content"
    liq_water.units = "gm/m^3"
    liq_water.missing_value = -99.0
    # W = (pi/6)*(1/F.t)*(sum(1 to 20)(ni.Di^3/v(Di)))
    # Wg = W/1000
    liq_water[:] = liq_water_g[:]

    # Variable: zdb / Formulas para encontrar obtidas do manual do instrumento
    zdb = inpeCDF.createVariable("zdb", "f4", ("time",))
    zdb.long_name = "Radar reflectivity"
    zdb.units = "dB"
    zdb.missing_value = -99.0
    zdb[:] = zdb_aux[:]

    # Variable: ef / Formulas para encontrar obtidas do manual do instrumento
    ef = inpeCDF.createVariable("ef", "f4", ("time",))
    ef.long_name = "Energy flux"
    ef.units = "J/(m^2-hr)"
    ef.missing_value = -99.0

    # Fluxo de energia
    ef[:] = ef_aux[:]

    # Variable: lambda / Formulas para encontrar obtidas do manual do instrumento
    slope = inpeCDF.createVariable(
        "lambda", "f4", ("time",)
    )  # lambda e uma palavra reservada
    slope.long_name = "Distribution slope"
    slope.units = "1/mm"
    slope.missing_value = -99.0
    slope[:] = slope_aux[:]

    # Variable: d_max / Formulas para encontrar obtidas do manual do instrumento
    d_max = inpeCDF.createVariable("d_max", "f4", ("time",))
    d_max.long_name = "Diameter of largest drop"
    d_max.units = "mm"
    d_max.missing_value = -99.0

    # Quanto maior a classe, maior o diametro medio
    d_max_aux = [0.0] * len(data)
    for i in range(0, len(data)):
        for t in reversed(range(0, 20)):
            if inpeCDF["num_drop"][i, t] != 0:
                d_max_aux[i] = mean_diam[t]
                break
            else:
                d_max_aux[i] = 0.0
    d_max[:] = d_max_aux[:]

    # Variable: nd / Formulas para encontrar obtidas do manual do instrumento
    nd = inpeCDF.createVariable("nd", "f4", ("time", "drop_class"))
    nd.long_name = "Number density"
    nd.units = "1/(m^3-mm)"
    nd.missing_value = -99.0

    for t in range(0, len(data)):
        for i in range(0, 20):
            nd[t, i] = (data["n" + str(i + 1)][t]) / (
                0.005 * 60 * velocity[i] * diam[i]
            )

    # Variable: n_0 / Formulas para encontrar obtidas do manual do instrumento
    n_0_aux = []
    reflect = 0.0
    for t in range(0, len(data)):
        for i in range(0, 20):
            reflect += (data["n" + str(i + 1)][t] * pow(mean_diam[i], 6)) / (
                velocity[i]
            )
        if reflect != 0:
            n_0_aux.append(
                (1 / math.pi)
                * pow((math.factorial(6) / math.pi), 4 / 3)
                * pow((liq_water_g[i] * 1000) / (reflect * (1 / (0.005 * 60))), 4 / 3)
                * (liq_water_g[i] * 1000)
            )
        else:
            n_0_aux.append(0.0)
        reflect = 0.0
    n_0 = inpeCDF.createVariable("n_0", "f4", ("time",))
    n_0.long_name = "Distribution intercept"
    n_0.units = "1/(m^3-mm)"
    n_0.missing_value = -99.0
    n_0[:] = n_0_aux[:]

    # Variable: precip_dis
    precip_dis_aux = []
    for i in range(0, len(data)):
        precip_dis_aux.append(data["RI [mm/h]"][i] * (60 / 3600))

    precip_dis = inpeCDF.createVariable("precip_dis", "f4", ("time",))
    precip_dis.long_name = "Precipitation"
    precip_dis.units = "mm"
    precip_dis.valid_min = 0.0
    precip_dis.valid_max = 10.0
    precip_dis.missing_value = -99.0
    precip_dis[:] = precip_dis_aux[:]

    # Variaveis de QC / Por enquanto, todas NaN

    qc_time = inpeCDF.createVariable("qc_time", "u4", ("time",))
    qc_time[:] = np.ma.masked

    qc_precip_dis = inpeCDF.createVariable("qc_precip_dis", "u4", ("time",))
    qc_precip_dis[:] = np.ma.masked

    qc_num_drop = inpeCDF.createVariable("qc_num_drop", "u4", ("time", "drop_class"))
    qc_num_drop[:] = np.ma.masked

    qc_rain_rate = inpeCDF.createVariable("qc_rain_rate", "u4", ("time",))
    qc_rain_rate[:] = np.ma.masked

    inpeCDF.close()


def Joss_GenerateGraph(readAddress, saveAddress):
    # Algoritmo para dados netCDF de duracao de 1 dia
    from netCDF4 import Dataset
    from netCDF4 import num2date
    from datetime import datetime
    from matplotlib.pyplot import subplots
    import matplotlib.pyplot as plt
    import matplotlib
    import numpy as np
    import pandas as pd
    import os
    import gc

    dataCDF = Dataset(readAddress, "r")
    matplotlib.use("Agg")  # Evita problema de Memory Leak
    # Seta o eixo temporal dos dados
    date = [np.ma.masked] * len(dataCDF["time_offset"][:])
    hours = ["--"] * len(dataCDF["time_offset"][:])
    for i in range(0, len(dataCDF["time_offset"][:])):
        date[i] = datetime.utcfromtimestamp(
            dataCDF["base_time"][:] + dataCDF["time_offset"][i]
        )
        hours[i] = (
            str("{:02}".format(date[i].hour))
            + ":"
            + str("{:02}".format(date[i].minute))
            + ":"
            + str("{:02}".format(date[i].second))
        )

    # Diretorio onde sera criado o folder com os plots
    plotFolder = (
        "JossPlots"
        + str("{:02}".format(date[0].day))
        + str("{:02}".format(date[0].month))
        + str("{:02}".format(date[0].year))
    )
    plotSaveAddress = os.path.join(saveAddress, plotFolder)
    os.makedirs(plotSaveAddress)  # Criacao da pasta

    # Graficos de variaveis unidimensionais
    def plot_1D(varName):
        varGraph = dataCDF[varName][:]
        fig, eixo = subplots()
        eixo.grid()
        eixo.set_title(
            dataCDF[varName].long_name
            + " from Disdrometer RD-80 - Day: "
            + str("{:02}".format(date[0].day))
            + "/"
            + str("{:02}".format(date[0].month))
            + "/"
            + str(date[0].year)
        )
        xTicks = np.arange(0, 1440, 60)
        eixo.set_xticks(xTicks)
        plt.xticks(rotation=50)
        eixo.set_ylabel(dataCDF[varName].units)
        eixo.plot(hours, varGraph)
        # Salva em png
        plt.tight_layout()  # saveAddress
        plt.savefig(
            plotSaveAddress
            + "\\"
            + varName
            + str("{:02}".format(date[0].day))
            + str("{:02}".format(date[0].month))
            + str("{:02}".format(date[0].year))
            + ".png"
        )
        plt.cla()
        plt.clf()
        plt.close("all")
        plt.close(fig)
        del fig
        del eixo
        gc.collect()

    # Densidade numerica de gotas minuto a minuto
    def plot_numDrop():
        for i in range(0, len(dataCDF["precip_dis"][:])):
            varGraph = dataCDF["nd"][i][:]
            totalDrops = 0
            for t in range(0, 19):
                totalDrops += dataCDF["nd"][i][t]
            precipCheck = dataCDF["rain_rate"][i]
            if precipCheck > (0.1) and totalDrops >= 10:
                fig, eixo = subplots()
                class_diam = dataCDF["mean_diam_drop_class"][:]
                eixo.grid()
                eixo.set_title(
                    "Number density from Disdrometer RD-80 - Day: "
                    + str("{:02}".format(date[i].day))
                    + "/"
                    + str("{:02}".format(date[i].month))
                    + "/"
                    + str(date[i].year)
                    + " - "
                    + str(hours[i])
                )
                xTicks = np.arange(0, 20, 1)
                eixo.set_xticks(xTicks)
                eixo.set_ylabel("N(D) " + dataCDF["nd"].units)
                eixo.set_xlabel("Diameter (mm)")
                eixo.set_yscale("log")
                eixo.plot(class_diam, varGraph)
                plt.tight_layout()
                plt.savefig(
                    plotSaveAddress
                    + "\\"
                    + "num_drop"
                    + str("{:02}".format(date[0].day))
                    + str("{:02}".format(date[0].month))
                    + str("{:02}".format(date[0].year))
                    + str(hours[i][0:2])
                    + str(hours[i][3:5])
                    + str(hours[i][6:8])
                    + ".png"
                )
                plt.cla()
                plt.clf()
                plt.close("all")
                plt.close(fig)
                del fig
                del eixo
                gc.collect()

    names1D = ["precip_dis", "rain_rate", "liq_water", "zdb", "ef", "lambda", "d_max"]

    for name in names1D:
        plot_1D(name)

    plot_numDrop()  # NOTA: Vai gerar muitos graficos (potencialmente 1 a cada minuto)

    dataCDF.close()