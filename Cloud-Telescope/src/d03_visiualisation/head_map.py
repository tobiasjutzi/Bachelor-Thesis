import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.axes_grid1 import make_axes_locatable
from src.d04_analysation.scanning import *
from src.config import *


def show_head_int_map_for_df(df: pd.DataFrame, y_index: str, x_columns: str, value_column: str, x_lable: str, y_lable,
                         save_name: str = 'default'):
    heatmap_data = df.pivot_table(index=y_index, columns=x_columns, values=value_column, aggfunc="mean")

    fig, ax = plt.subplots(figsize=(8, 6))

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("bottom", size="5%", pad=0.5)

    heatmap = sns.heatmap(heatmap_data, cmap="magma", linewidths=0.5, linecolor='gray', cbar=True, ax=ax, cbar_ax=cax,
                          cbar_kws={'orientation': 'horizontal', 'label': 'Anzahl Angriffe'})

    cbar = heatmap.collections[0].colorbar
    min_val, max_val = heatmap_data.min().min(), heatmap_data.max().max()
    ticks = np.arange(np.floor(min_val), np.ceil(max_val) + 1, 1)
    cbar.set_ticks(ticks)
    cbar.set_ticklabels([str(int(tick)) for tick in ticks])

    ax.set_xlabel(x_lable)
    ax.set_ylabel(y_lable)

    plt.savefig(f"{path_root}/Cloud-Telescope/data/diagramms/{save_name}_heatmap.pdf", bbox_inches='tight')

    return plt


def show_heat_convert_map_for_df(df: pd.DataFrame, y_index: str, x_columns: str, value_column: str,
                         x_label: str, y_label: str, save_name: str = 'default', color_scale_description: str = 'Scanner',
                         convert_seconds_to_minutes: bool = True):
    """
    Parameter:
    - df: Pandas DataFrame mit den Daten
    - y_index: Spalte für die Y-Achse
    - x_columns: Spalte für die X-Achse (entweder Sekunden oder Minuten)
    - value_column: Spalte mit den Werten für die Heatmap
    - x_label, y_label: Achsenbeschriftungen
    - save_name: Name der gespeicherten Datei
    - convert_seconds_to_minutes: Falls True, werden Sekunden in Minuten konvertiert
    """

    if convert_seconds_to_minutes:
        df[x_columns] = df[x_columns] // 60

    heatmap_data = df.pivot_table(index=y_index, columns=x_columns, values=value_column, aggfunc="mean")

    fig, ax = plt.subplots(figsize=(8, 6))

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("bottom", size="5%", pad=0.5)

    sns.heatmap(heatmap_data, cmap="magma", linewidths=0.5, linecolor='gray',
                cbar=True, ax=ax, cbar_ax=cax,
                cbar_kws={'orientation': 'horizontal', 'label': color_scale_description})

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    plt.savefig(f"{path_root}/Cloud-Telescope/data/diagramms/{save_name}_heatmap.pdf", bbox_inches='tight')

    return plt


