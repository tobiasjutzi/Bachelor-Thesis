import pandas as pd
import matplotlib.pyplot as plt
from src.config import *

import pandas as pd
import matplotlib.pyplot as plt


def show_as_basic_table(df: pd.DataFrame, col_widths: dict, row_heights: list, col_left_offsets: dict):
    fig, ax = plt.subplots()
    ax.axis("tight")
    ax.axis("off")

    formatted_values = df.copy()
    if "Dns_Eintrag" in formatted_values.columns:
        formatted_values["Dns_Eintrag"] = formatted_values["Dns_Eintrag"].apply(
            lambda x: "\n".join(x.split(", "))
        )

    table = ax.table(cellText=formatted_values.values,
                     colLabels=df.columns,
                     cellLoc="left",
                     loc="center")

    table.auto_set_font_size(False)
    table.set_fontsize(10)

    for j in range(len(df) + 1):
        height = row_heights[j] if j < len(row_heights) else 0.5
        for i in range(len(df.columns)):
            table._cells[(j, i)].set_height(height)

    for i, col in enumerate(df.columns):
        if col in col_widths:
            for j in range(len(df) + 1):
                table._cells[(j, i)].set_width(col_widths[col])

    for i, col in enumerate(df.columns):
        if col in col_left_offsets:
            offset = col_left_offsets[col]
            for j in range(len(df) + 1):
                cell = table._cells[(j, i)]
                text = cell.get_text()
                text.set_ha("left")
                text.set_position((offset, 0.5))

    plt.savefig("education_table.pdf", bbox_inches='tight')
    return plt


def show_two_basic_table(df: pd.DataFrame, col_widths: dict, row_heights: list, saving_name: str):
    fig, ax = plt.subplots()
    ax.axis("tight")
    ax.axis("off")

    table = ax.table(cellText=df.values.tolist(), colLabels=df.columns, cellLoc="left", loc="center")


    table.auto_set_font_size(False)
    table.set_fontsize(10)

    for j in range(len(df) + 1):
        height = row_heights[j] if j < len(row_heights) else 0.5
        for i in range(len(df.columns)):
            table._cells[(j, i)].set_height(height)

    for i, col in enumerate(df.columns):
        if col in col_widths:
            for j in range(len(df) + 1):
                table._cells[(j, i)].set_width(col_widths[col])

    plt.savefig(f"{path_root}/Cloud-Telescope/data/diagramms/{saving_name}.pdf", bbox_inches='tight')
    return plt
