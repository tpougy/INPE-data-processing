from datetime import datetime, timedelta

import numpy as np

from netCDF4 import Dataset

import time

import kaleido
import psutil
import plotly.graph_objects as go

from pathlib import Path

import argparse

import os
import sys

########################## AUXILIAR FUNCTIONS #######################################


def log_RR(dbz):
    return ((10 ** (dbz / 10)) / (200)) ** (1 / 1.6)


# sourcery skip: hoist-statement-from-loop
converter2datetime = np.vectorize(
    lambda x: datetime.utcfromtimestamp(dataR["base_time"][:] + x)
)


########################### VARIABLE NAMES ##########################################

PIA_longname = "Path Integrated Attenuation"
PIA_unit = "dB"

Z_longname = "Radar Reflectivity"
Z_unit = "dBZ"

z_longname = "Attenuated Radar Reflectivity"
z_unit = "dBZ"

RR_longname = "Rain Rate"
RR_unit = "mm*h^(-1)"

LWC_longname = "Liquid Water Contents"
LWC_unit = "g*m^(-3)"

W_longname = "Fall fall_vell"
W_unit = "m*s^(-1)"

############################# SCALES ############################################

arm_colorscale = [
    [0, "#656563"],
    [5 / 75, "#04e4ea"],
    [10 / 75, "#009ef2"],
    [15 / 75, "#0400f0"],
    [20 / 75, "#04ff04"],
    [25 / 75, "#01c602"],
    [30 / 75, "#008d00"],
    [35 / 75, "#fef601"],
    [40 / 75, "#e5bc00"],
    [45 / 75, "#fe9503"],
    [50 / 75, "#fd0002"],
    [55 / 75, "#ce0300"],
    [60 / 75, "#ba0000"],
    [65 / 75, "#f700fe"],
    [70 / 75, "#9655c9"],
    [75 / 75, "#f5fef8"],
]

arm_colorscale_RR = [
    [0, "#656563"],
    [log_RR(5) / log_RR(75), "#04e4ea"],
    [log_RR(10) / log_RR(75), "#009ef2"],
    [log_RR(15) / log_RR(75), "#0400f0"],
    [log_RR(20) / log_RR(75), "#04ff04"],
    [log_RR(25) / log_RR(75), "#01c602"],
    [log_RR(30) / log_RR(75), "#008d00"],
    [log_RR(35) / log_RR(75), "#fef601"],
    [log_RR(40) / log_RR(75), "#e5bc00"],
    [log_RR(45) / log_RR(75), "#fe9503"],
    [log_RR(50) / log_RR(75), "#fd0002"],
    [log_RR(55) / log_RR(75), "#ce0300"],
    [log_RR(60) / log_RR(75), "#ba0000"],
    [1, "#f5fef8"],
]


dummy_colorscale_RR = [
    [0, "#656563"],
    [1 / 13, "#04e4ea"],
    [2 / 13, "#009ef2"],
    [3 / 13, "#0400f0"],
    [4 / 13, "#04ff04"],
    [5 / 13, "#01c602"],
    [6 / 13, "#008d00"],
    [7 / 13, "#fef601"],
    [8 / 13, "#e5bc00"],
    [9 / 13, "#fe9503"],
    [10 / 13, "#fd0002"],
    [11 / 13, "#ce0300"],
    [12 / 13, "#ba0000"],
    [13 / 13, "#f5fef8"],
]

######################### READING EXECUTION FLAGS ##########################

# Create the parser
MRR_parser = argparse.ArgumentParser(
    description="Generate figures for MRR netCDF files"
)

# Add the arguments
MRR_parser.add_argument("-v", "--version", action="version", version="%(prog)s 0.1")

MRR_parser.add_argument(
    "-a",
    "--auto",
    action="store_true",
    default=None,
    help="Executes the script in auto-mode, based on the log files",
)

MRR_parser.add_argument(
    "-f",
    "--file",
    action="store",
    type=str,
    nargs=1,
    default=None,
    help="Executes the script for the file specified",
)

MRR_parser.add_argument(
    "-l",
    "--list",
    action="store",
    type=str,
    nargs=1,
    default=None,
    help="Executes the script for an arbitrary list (txt) of files. The list file must have the absolute position of the files in each line.",
)

# Execute the parse_args() method
args = MRR_parser.parse_args()

# check if there is at least one action requested
if args.auto is None and args.file is None and args.list is None:
    MRR_parser.error("No action requested, see --help to further information")

################# GENERATING FILES LIST BASED OF EXECUTION FLAGS ##################

if args.auto is not None:
    print("Executing the script in auto mode")

    generated_cdf = [line.rstrip() for line in open("./output/MRR/MRR_netCDF.log")]
    generated_cdf = [generated_cdf[i][20:] for i in range(len(generated_cdf))]
    generated_cdf = [
        generated_cdf[i]
        for i in range(len(generated_cdf))
        if (generated_cdf[i].find("raw") == -1)
    ]

    generated_figures = [line.rstrip() for line in open("./output/MRR/MRR_figures.log")]
    generated_figures = [
        generated_figures[i][20:] for i in range(len(generated_figures))
    ]

    files_list = np.setdiff1d(generated_cdf, generated_figures).tolist()

if args.file is not None:
    files_list = []
    files_list[0] = args.file[0]

if args.list is not None:
    files_list = [line.rstrip() for line in open(args.list[0])]


############################# LOOP FILES LIST ###################################

for i in range(len(files_list)):

    cdf_filename = files_list[i]

    input_folder = "input/MRR/data_figures"

    # reading netCDF file
    dataR = Dataset("./" + input_folder + "/" + cdf_filename, "r")

    # necessary command when reading the netCDF file, forces the variables ot be read as simple numpy array (not masked)
    dataR.set_auto_mask(False)

    print(" ")
    print("File read: " + cdf_filename)

    output_folder = "output/MRR/figures/" + cdf_filename[0 : len(cdf_filename) - 3]
    Path("./" + output_folder).mkdir(parents=True, exist_ok=True)

    ############################### FIGURE 1 ############################################
    # Figure for z

    fig1 = go.Figure(
        data=go.Heatmap(
            z=dataR["z"][:, :].transpose(),
            x=converter2datetime(dataR["time_offset"][:]),
            y=dataR["height"][0, :],
            zsmooth="best",
            zmin=0,
            zmax=75,
            connectgaps=False,
            colorscale=arm_colorscale,
            colorbar=dict(
                title=dict(text=(z_longname + " (z) " + z_unit), side="right")
            ),
        )
    )

    fig1.update_xaxes(nticks=12)

    fig1.update_layout(title="MRR - " + z_longname + " (z) [" + z_unit + "]")

    fig1.update_yaxes(title_text="Altitudes [m]")

    fig1_filename = "./" + output_folder + "/" + "fig_z_" + cdf_filename[:-3] + ".png"
    html1_filename = (
        "./" + output_folder + "/" + "html_z_" + cdf_filename[:-3] + ".html"
    )

    fig1.write_image(fig1_filename)
    fig1.write_html(html1_filename, include_plotlyjs="cdn")

    print("Figure generated for: " + z_longname)

    ############################# FIGURE 2 ############################################
    # Figure for RR

    # we used a trick to make the colorbar legible for the logarithmic values of the variable plotted
    # we generated a dummy plot (blank) with a linear colorbar and used ticktext to overwrite the 0 to 13 values with the representative values realted to the actual plot
    # then we disabled the colorbar for the actual plot
    # and for the last step we used fig2.add_trace to add the colorbar dummy plot to the actual plot

    colorbar_trace = go.Scatter(
        x=[None],
        y=[None],
        mode="markers",
        marker=dict(
            colorscale=dummy_colorscale_RR,
            cmin=0,
            cmax=13,
            colorbar=dict(
                title=dict(text=(RR_longname + " (RR) " + RR_unit), side="right"),
                tickmode="array",
                tickvals=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
                ticktext=[
                    "0.04",
                    "0.07",
                    "0.15",
                    "0.32",
                    "0.65",
                    "1.33",
                    "2.73",
                    "5.62",
                    "11.53",
                    "23.68",
                    "48.62",
                    "99.85",
                    "205.5",
                    "421.07",
                ],
            ),
        ),
        hoverinfo="none",
    )

    fig2 = go.Figure(
        data=go.Heatmap(
            z=dataR["RR"][:, :].transpose(),
            x=converter2datetime(dataR["time_offset"][:]),
            y=dataR["height"][0, :],
            zsmooth="best",
            zmin=0,
            zmax=421.07,
            connectgaps=False,
            showscale=False,
            colorscale=arm_colorscale_RR,
        )
    )

    fig2.update_xaxes(nticks=12)

    fig2.update_layout(title="MRR - " + RR_longname + " (RR) [" + RR_unit + "]")

    fig2.update_yaxes(title_text="Altitudes [m]")

    fig2.add_trace(colorbar_trace)

    fig2_filename = "./" + output_folder + "/" + "fig_RR_" + cdf_filename[:-3] + ".png"
    html2_filename = (
        "./" + output_folder + "/" + "html_RR_" + cdf_filename[:-3] + ".html"
    )

    fig2.write_image(fig2_filename)
    fig2.write_html(html2_filename, include_plotlyjs="cdn")

    print("Figure generated for: " + RR_longname)

    ############################# FIGURE 3 ############################################
    # Figure for LWC

    fig3 = go.Figure(
        data=go.Heatmap(
            z=dataR["LWC"][:, :].transpose(),
            x=converter2datetime(dataR["time_offset"][:]),
            y=dataR["height"][0, :],
            zsmooth="best",
            connectgaps=False,
            colorscale=arm_colorscale,
            colorbar=dict(
                title=dict(text=(LWC_longname + " (LWC) " + LWC_unit), side="right")
            ),
        )
    )

    fig3.update_xaxes(nticks=12)

    fig3.update_layout(title="MRR - " + LWC_longname + " (LWC) [" + LWC_unit + "]")

    fig3.update_yaxes(title_text="Altitudes [m]")

    fig3_filename = "./" + output_folder + "/" + "fig_LWC_" + cdf_filename[:-3] + ".png"
    html3_filename = (
        "./" + output_folder + "/" + "html_LWC_" + cdf_filename[:-3] + ".html"
    )

    fig3.write_image(fig3_filename)
    fig3.write_html(html3_filename, include_plotlyjs="cdn")

    print("Figure generated for: " + LWC_longname)

    ############################### FIGURE 4 ############################################
    # Figure for W

    fig4 = go.Figure(
        data=go.Heatmap(
            z=dataR["W"][:, :].transpose(),
            x=converter2datetime(dataR["time_offset"][:]),
            y=dataR["height"][0, :],
            zsmooth="best",
            zmin=0,
            zmax=10,
            connectgaps=False,
            colorscale=arm_colorscale,
            colorbar=dict(
                title=dict(text=(W_longname + " (W) " + W_unit), side="right")
            ),
        )
    )

    fig4.update_xaxes(nticks=12)

    fig4.update_layout(title="MRR - " + W_longname + " (W) [" + W_unit + "]")

    fig4.update_yaxes(title_text="Altitudes [m]")

    fig4_filename = "./" + output_folder + "/" + "fig_W_" + cdf_filename[:-3] + ".png"
    html4_filename = (
        "./" + output_folder + "/" + "html_W_" + cdf_filename[:-3] + ".html"
    )

    fig4.write_image(fig4_filename)
    fig4.write_html(html4_filename, include_plotlyjs="cdn")

    print("Figure generated for: " + W_longname)

    # ######################### CLOSING FILE #########################################

    dataR.close

    # register what file has been generated
    creation_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("./output/MRR/MRR_figures.log", "a") as f:
        f.write(creation_datetime + "|" + cdf_filename + "\n")
