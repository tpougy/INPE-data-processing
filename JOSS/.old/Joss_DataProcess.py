# Processador de dados do disdrometro JOSS
import numpy as np
import pandas as pd
import csv
from datetime import datetime, timedelta
import os
import time
import math
from netCDF4 import Dataset
from netCDF4 import num2date
import pathlib
from Joss_Utilities import Joss_GenerateCDF
from Joss_Utilities import Joss_GenerateGraph

pathName = str(pathlib.Path(__file__).parent.absolute())
files = [file for file in os.listdir(pathName) if file.endswith(".trf")]

dataFrames = []  # Dataframes do pandas para cada arquivo
fullAddr = [os.path.join(pathName, file) for file in files]

for i in range(len(files[:])):
    fileData = pd.read_csv(
        fullAddr[i],
        sep="\s",
        header=None,
        names=[
            "YYYY-MM-DD",
            "hh:mm:ss",
            "Status",
            "Interval [s]",
            "n1",
            "n2",
            "n3",
            "n4",
            "n5",
            "n6",
            "n7",
            "n8",
            "n9",
            "n10",
            "n11",
            "n12",
            "n13",
            "n14",
            "n15",
            "n16",
            "n17",
            "n18",
            "n19",
            "n20",
            "RI [mm/h]",
            "RA [mm]",
            "RAT [mm]",
        ],
        skiprows=[0],
        index_col=False,
        engine="python",
    )
    dataFrames.append(fileData)

# Juncao de todos os dataframes individuais em um maior e sort por datas
bigFrame = pd.concat(dataFrames[:], ignore_index=True)
bigFrame["Dates"] = pd.to_datetime(
    bigFrame["YYYY-MM-DD"][:] + " " + bigFrame["hh:mm:ss"][:], utc=True
)  #'Dates' = Nova col datetimes
bigFrame = bigFrame.sort_values(by="Dates")

# Mudar ',' para '.' e interpretar RI,RA,RAT como floats (e nao strings)
bigFrame["RI [mm/h]"] = bigFrame["RI [mm/h]"].replace(",", ".", regex=True)
bigFrame["RA [mm]"] = bigFrame["RA [mm]"].replace(",", ".", regex=True)
bigFrame["RAT [mm]"] = bigFrame["RAT [mm]"].replace(",", ".", regex=True)

bigFrame["RI [mm/h]"] = bigFrame["RI [mm/h]"].astype("float64")
bigFrame["RA [mm]"] = bigFrame["RA [mm]"].astype("float64")
bigFrame["RAT [mm]"] = bigFrame["RAT [mm]"].astype("float64")

# Cria-se um vetor com todos os datetimes desde a primeira medicao ate a meia noite do mesmo dia
timeBufferBack = []
startTimeBack = pd.to_datetime(bigFrame["YYYY-MM-DD"][0] + " 00:00:00", utc=True)
if bigFrame["Dates"][0] > startTimeBack:
    t = 0
    while (startTimeBack + timedelta(minutes=t)) != bigFrame["Dates"][0]:
        timeBufferBack.append(startTimeBack + timedelta(minutes=t))
        t += 1

timeBufferFront = []
endTimeFront = pd.to_datetime(
    bigFrame["YYYY-MM-DD"][(len(bigFrame["Dates"]) - 1)] + " 23:59:00", utc=True
)
if bigFrame["Dates"][(len(bigFrame["Dates"]) - 1)] < endTimeFront:
    t = 1
    while (endTimeFront - timedelta(minutes=t - 1)) != bigFrame["Dates"][
        (len(bigFrame["Dates"]) - 1)
    ]:
        timeBufferFront.append(
            bigFrame["Dates"][(len(bigFrame["Dates"]) - 1)] + timedelta(minutes=t)
        )
        t += 1

# Cria-se dataframes a serem unidos ao maior, com valores indef
names = [
    "YYYY-MM-DD",
    "hh:mm:ss",
    "Status",
    "Interval [s]",
    "n1",
    "n2",
    "n3",
    "n4",
    "n5",
    "n6",
    "n7",
    "n8",
    "n9",
    "n10",
    "n11",
    "n12",
    "n13",
    "n14",
    "n15",
    "n16",
    "n17",
    "n18",
    "n19",
    "n20",
    "RI [mm/h]",
    "RA [mm]",
    "RAT [mm]",
    "Dates",
]

datesBack = [timeBufferBack[i].date() for i in range(len(timeBufferBack[:]))]
timesBack = [timeBufferBack[i].time() for i in range(len(timeBufferBack[:]))]
datesFront = [timeBufferFront[i].date() for i in range(len(timeBufferFront[:]))]

timesFront = [timeBufferFront[i].time() for i in range(len(timeBufferFront[:]))]

dataBack = {
    "YYYY-MM-DD": datesBack,
    "hh:mm:ss": timesBack,
    "Status": np.NaN,
    "Interval [s]": 60,
    "n1": 0,
    "n2": 0,
    "n3": 0,
    "n4": 0,
    "n5": 0,
    "n6": 0,
    "n7": 0,
    "n8": 0,
    "n9": 0,
    "n10": 0,
    "n11": 0,
    "n12": 0,
    "n13": 0,
    "n14": 0,
    "n15": 0,
    "n16": 0,
    "n17": 0,
    "n18": 0,
    "n19": 0,
    "n20": 0,
    "RI [mm/h]": 0.0000,
    "RA [mm]": 0.0000,
    "RAT [mm]": 0.0000,
    "Dates": np.NaN,
}

frameBack = pd.DataFrame(dataBack, columns=names)

dataFront = {
    "YYYY-MM-DD": datesFront,
    "hh:mm:ss": timesFront,
    "Status": np.NaN,
    "Interval [s]": 60,
    "n1": 0,
    "n2": 0,
    "n3": 0,
    "n4": 0,
    "n5": 0,
    "n6": 0,
    "n7": 0,
    "n8": 0,
    "n9": 0,
    "n10": 0,
    "n11": 0,
    "n12": 0,
    "n13": 0,
    "n14": 0,
    "n15": 0,
    "n16": 0,
    "n17": 0,
    "n18": 0,
    "n19": 0,
    "n20": 0,
    "RI [mm/h]": 0.0000,
    "RA [mm]": 0.0000,
    "RAT [mm]": 0.0000,
    "Dates": np.NaN,
}

frameFront = pd.DataFrame(dataFront, columns=names)

# Unir dataframes indef com o dataframe maior
if (
    bigFrame["Dates"][0] > startTimeBack
    and bigFrame["Dates"][(len(bigFrame["Dates"]) - 1)] < endTimeFront
):
    bigFrameFull = pd.concat([bigFrame, frameFront], ignore_index=True)
    bigFrameFull = pd.concat([frameBack, bigFrameFull], ignore_index=True)
elif bigFrame["Dates"][0] > startTimeBack:
    bigFrameFull = pd.concat([frameBack, bigFrame], ignore_index=True)
elif bigFrame["Dates"][(len(bigFrame["Dates"]) - 1)] < endTimeFront:
    bigFrameFull = pd.concat([bigFrame, frameFront], ignore_index=True)
else:
    bigFrameFull = bigFrame

# Separar dataframes por dia
dataPerDay = [
    bigFrameFull[:][1440 * (i - 1) : (1440 * i)] for i in range(1, len(files[:]) + 2)
]

for i in range(len(dataPerDay[:])):
    dataPerDay[i] = (dataPerDay[i].reset_index()).drop(columns=["index", "Dates"])

for i in range(len(dataPerDay[:])):
    Joss_GenerateCDF(
        dataPerDay[i], pathName
    )  # Chama a funcao do Joss_Utilities para gerar os CDFs por dia

cdfFiles = [file for file in os.listdir(pathName) if file.endswith(".nc")]
cdfFullAddr = [os.path.join(pathName, file) for file in cdfFiles]
for cdfAddress in cdfFullAddr:
    Joss_GenerateGraph(
        cdfAddress, pathName
    )  # Chama a funcao do Joss_Utilities para gerar os plots para cada arquivo CDF
