import datetime
from datetime import timedelta
import numpy as np
import kaleido
import psutil
import plotly.graph_objects as go


def figures_to_html(figs, filename="dashboard.html"):
    dashboard = open(filename, "w")
    dashboard.write("<html><head></head><body>" + "\n")
    for fig in figs:
        inner_html = fig.to_html().split("<body>")[1].split("</body>")[0]
        dashboard.write(inner_html)
    dashboard.write("</body></html>" + "\n")


def gen_fig_NDropxDi(time_index, data1, index2, data2, fig_metadata, output_folder):

    # Fig1 is the figure for the Rain Rate
    layout1 = go.Layout(autosize=False, width=1000, height=450)

    notes1 = []

    notes1.append(
        {
            "text": (
                "Disdrometer: {}<br>Site: {}<br>".format(
                    fig_metadata["disdrometer"], fig_metadata["site"]
                )
            ),
            "x": 0.00,
            "y": 1.55,
            "xref": "paper",
            "yref": "paper",
            "showarrow": False,
            "font": {"size": 14},
            "align": "left",
        }
    )

    notes1.append(
        {
            "text": (
                "Data file: {}<br>Generated at: {}<br>".format(
                    output_folder.name + ".nc",
                    datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S"),
                )
            ),
            "x": 0.00,
            "xshift": 250,
            "y": 1.55,
            "xref": "paper",
            "yref": "paper",
            "showarrow": False,
            "font": {"size": 14},
            "align": "left",
        }
    )

    notes1.append(
        {
            "text": "Rain Rate - RD-80 (Joss-Waldvogel)",
            "x": 0.00,
            "y": 1.20,
            "xref": "paper",
            "yref": "paper",
            "showarrow": False,
            "font": {"size": 18},
        }
    )

    layout1["annotations"] = notes1
    layout1["margin"] = {"t": 150}

    fig1 = go.Figure(layout=layout1)

    fig1.add_trace(
        go.Scatter(
            x=time_index,
            y=data1[:],
        )
    )

    fig1.update_yaxes(title_text="Rain Rate (mm/h)")
    # Fig2 is the figure for the NDrop x Di
    # data2 = file_data["Number of raindrops"][sec][:]
    # index2 = variables_info["drop_class"]
    notes2 = []

    notes2.append(
        {
            "text": "N(D) x Diameter",
            "x": 0.00,
            "y": 1.15,
            "xref": "paper",
            "yref": "paper",
            "showarrow": False,
            "font": {"size": 18},
        }
    )

    # Setup the layout.
    layout2 = go.Layout(autosize=False, width=1000, height=600)
    layout2["annotations"] = notes2
    layout2["margin"] = {"t": 160}

    fig2 = go.Figure(layout=layout2)

    # Add traces, one for each slider step
    for sec in np.arange(0, 1440, 1):
        fig2.add_trace(
            go.Scatter(
                visible=False,
                name="({})".format(
                    (time_index[0] + timedelta(minutes=int(sec))).strftime("%H:%M")
                ),
                x=index2,
                y=data2[sec][:],
            ),
        )

    # Make 10th trace visible
    fig2.data[0].visible = True

    # Create and add slider
    steps = []
    for i in range(len(fig2.data)):
        label_aux = time_index[0] + timedelta(minutes=i)
        step = dict(
            method="update",
            label=label_aux.strftime("%H:%M"),
            args=[
                {"visible": [False] * len(fig2.data)},
            ],  # layout attribute
        )
        step["args"][0]["visible"][i] = True  # Toggle i'th trace to "visible"
        steps.append(step)

    sliders = [
        dict(
            active=0,
            currentvalue={
                "prefix": "{} - Time: ".format(time_index[0].strftime("%b %d,%Y"))
            },
            # pad={"t": 50},
            steps=steps,
        )
    ]

    fig2.update_layout(sliders=sliders)

    fig2["layout"]["sliders"][0]["pad"] = dict(
        t=-500,
    )

    # update axes
    fig2.update_xaxes(title_text="Diameter (mm)", nticks=40)
    fig2.update_yaxes(title_text="N(D) (m⁻³ mm⁻¹)", type="log")

    # Generate the figure
    html_filename = "html_RR_NDropxDi_{}.html".format(output_folder.name)

    figures_to_html([fig1, fig2], filename=output_folder.joinpath(html_filename))


def gen_fig_1D(data, index, var, unit, fig_metadata, output_folder, flag_png):

    layout = go.Layout(autosize=False, width=1000, height=450)

    notes = []

    notes.append(
        {
            "text": (
                "Disdrometer: {}<br>Site: {}<br>".format(
                    fig_metadata["disdrometer"], fig_metadata["site"]
                )
            ),
            "x": 0.00,
            "y": 1.55,
            "xref": "paper",
            "yref": "paper",
            "showarrow": False,
            "font": {"size": 14},
            "align": "left",
        }
    )

    notes.append(
        {
            "text": (
                "Data file: {}<br>Generated at: {}<br>".format(
                    output_folder.name + ".nc",
                    datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S"),
                )
            ),
            "x": 0.00,
            "xshift": 250,
            "y": 1.55,
            "xref": "paper",
            "yref": "paper",
            "showarrow": False,
            "font": {"size": 14},
            "align": "left",
        }
    )

    notes.append(
        {
            "text": "RD-80 - {} ({})".format(var, unit),
            "x": 0.00,
            "y": 1.20,
            "xref": "paper",
            "yref": "paper",
            "showarrow": False,
            "font": {"size": 18},
        }
    )

    layout["annotations"] = notes
    layout["margin"] = {"t": 150}

    fig = go.Figure(layout=layout)

    # add title
    # fig.update_layout(title="JOSS - {} ({})".format(var, unit))

    # add data trace
    fig.add_trace(go.Scatter(x=index, y=data, mode="lines"))

    # update axes
    fig.update_xaxes(nticks=24)
    fig.update_yaxes(title_text="{} ({})".format(var, unit))

    # generate file names
    png_filename = "fig_{}_{}.png".format(
        var.lower().replace(" ", "_"), output_folder.name
    )
    html_filename = "html_{}_{}.html".format(
        var.lower().replace(" ", "_"), output_folder.name
    )

    # export figures as files
    fig.write_image(output_folder.joinpath(png_filename))
    if not flag_png:
        fig.write_html(output_folder.joinpath(html_filename), include_plotlyjs="cdn")
