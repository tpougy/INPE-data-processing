from .utils_files import *
from .utils_variables import *

import pandas as pd
from datetime import timedelta


def parse_files(files, export_date, variables_info):

    # only for support, numbers are not used for anything
    var_essential = [9, 20 + 21, 25, 93]
    var_interest = [1, 7, 9, 13, 20 + 21, 25, 93]

    # initializing variables for the loop
    files_data = []

    for file in files:

        idx_lines, lines = parse_flines(file)

        init_mask = [1]
        # adiciona no final de init_positions um vetor com a posição da ultima linha do vetor lines
        # importante para o loop de parse das variaveis varrer o ultimo bloco
        init_positions = find_sub_list(init_mask, idx_lines) + [len(lines)]

        i = 0
        var_comp = []

        for i_pos in init_positions[1:]:
            var_iteration = [None for _ in var_interest]

            while i < i_pos:
                # normal variable
                if lines[i]["idx"] == 1:
                    var_iteration[0] = parse_ri(lines[i]["value"])

                # normal variable
                elif lines[i]["idx"] == 7:
                    var_iteration[1] = parse_z(lines[i]["value"])

                #### essential variable ####
                elif lines[i]["idx"] == 9:
                    var_iteration[2] = parse_sample_interval(lines[i]["value"])

                # normal variable
                elif lines[i]["idx"] == 13:
                    var_iteration[3] = parse_serial(lines[i]["value"])

                #### essential variable ####
                elif lines[i]["idx"] == 20:
                    time_aux = lines[i]["value"]
                elif lines[i]["idx"] == 21:
                    date_aux = lines[i]["value"]
                    var_iteration[4] = parse_datetime(f"{date_aux} {time_aux}")

                #### essential variable ####
                elif lines[i]["idx"] == 25:
                    var_iteration[5] = parse_erro(lines[i]["value"])

                #### essential variable ####
                elif lines[i]["idx"] == 93:
                    var_iteration[6] = parse_vpd(
                        lines[i]["value"], variables_info["vpd_mask"]
                    )

                i += 1

            # Check if any essential variable is None in the block
            if None in [
                var_iteration[2],
                var_iteration[4],
                var_iteration[5],
                var_iteration[6],
            ]:
                var_comp.append([None for _ in var_interest])
            else:
                var_comp.append(var_iteration)

            files_data.append(
                pd.DataFrame.from_records(
                    var_comp,
                    columns=[
                        "ri",
                        "z",
                        "sample_interval",
                        "serial",
                        "datetime",
                        "erro",
                        "vpd",
                    ],
                    index="datetime",
                )
            )

    all_data = pd.concat(files_data)

    if export_date is None:
        export_date = all_data.index[0]

    datei = datetime(export_date.year, export_date.month, export_date.day, 0, 0)
    datef = datetime(export_date.year, export_date.month, export_date.day, 23, 59)

    mask = (all_data.index > datei) & (all_data.index <= datef)

    day_data = all_data.loc[mask]

    return day_data, export_date + timedelta(days=1), export_date > all_data.index[-1]
