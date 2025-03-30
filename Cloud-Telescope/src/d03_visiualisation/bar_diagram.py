import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import cm
from mpl_toolkits.axes_grid1 import make_axes_locatable
from src.d04_analysation.scanning import *
#from brokenaxes import brokenaxes
from matplotlib.ticker import FuncFormatter


def basic_bar_diagram(df: pd.DataFrame, x_column: str, y_column: str, x_lable: str, y_lable: str):
    plt.figure(figsize=(10, 5))
    plt.bar(df[x_column], df[y_column], color='skyblue')

    plt.xlabel(x_lable)
    plt.ylabel(y_lable)

    plt.xticks(rotation=75)

    # Diagramm anzeigen
    return plt


def basic_bar_new_2_diagram(df: pd.DataFrame, x_column: str, y_column: str, x_label: str, y_label: str,
                          rotation: int = 75, saving_name: str = 'protocol', width: float = 0.5,
                          bar_spacing: float = 0.2, diagramm_width: float = 10.0, diagramm_height: float = 5.0):
    plt.figure(figsize=(diagramm_width, diagramm_height))

    x_values = range(len(df[x_column]))
    adjusted_x = [x * (1 + bar_spacing) for x in x_values]

    plt.bar(adjusted_x, df[y_column], color='skyblue', width=width)

    plt.xlabel(x_label)
    plt.ylabel(y_label)

    plt.xticks(adjusted_x, df[x_column], rotation=rotation, ha='right', rotation_mode='anchor')

    y_min, y_max = plt.ylim()
    plt.yticks(np.arange(np.ceil(y_min), np.floor(y_max) + 1, 1))

    plt.savefig(f"{path_root}/Cloud-Telescope/data/diagramms/{saving_name}_bar_diagram.pdf", bbox_inches='tight')
    return plt


def seaborn_bar_diagram(df: pd.DataFrame, x_column: str, y_column: str, x_lable: str, y_lable: str, rotation: int, saving_name: str):
    plt.figure(figsize=(12, 6))
    sns.barplot(data=df, x=x_column, y=y_column, color='steelblue')
    plt.xticks(rotation=rotation, ha="right")

    plt.xlabel(x_lable)
    plt.ylabel(y_lable)
    plt.savefig(f"{path_root}/Cloud-Telescope/data/diagramms/{saving_name}_bar_diagram.pdf", bbox_inches='tight')
    return plt

# ja
def seaborn_bar2_diagram(df: pd.DataFrame, x_column: str, y_column: str, x_lable: str, y_lable: str, rotation: int,
                        saving_name: str, set_position: float = 0.9):
    plt.figure(figsize=(12, 6))
    ax = sns.barplot(data=df, x=x_column, y=y_column, color='steelblue')
    plt.xticks(rotation=rotation, ha="right")

    dpi_trans = plt.gcf().dpi_scale_trans
    offset = mtransforms.ScaledTranslation(5 / 72, 0, dpi_trans)

    for label in ax.get_xticklabels():
        label.set_transform(label.get_transform() + offset)

    plt.xlabel(x_lable)
    plt.ylabel(y_lable)
    plt.savefig(f"{path_root}/Cloud-Telescope/data/diagramms/{saving_name}_bar_diagram.pdf", bbox_inches='tight')
    return plt


def multi_bar_diagram(df: pd.DataFrame, x_column: str, y_columns: list[str], x_label: str, y_label: str, y_descriptions: list[str], bar_width: float = 0.4, rotation: int = 0):
    x = np.arange(len(df[x_column]))
    width = bar_width

    fig, ax = plt.subplots(figsize=(10, 5))

    total_y_columns = len(y_columns)
    cmap = plt.get_cmap("tab10")

    for i, y_column in enumerate(y_columns):
        color = cmap(i / total_y_columns)
        ax.bar(x + (i - (total_y_columns - 1) / 2) * width, df[y_column], width, label=y_descriptions[i], color=color)

    ax.set_xticks(x)
    ax.set_xticklabels(df[x_column])

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.legend()

    if rotation != 0:
        plt.xticks(rotation=rotation)

    return plt


def multi_color_new2_bar_diagram(df: pd.DataFrame, x_column: str, y_columns: list[str],
                                x_label: str, y_label: str, y_descriptions: list[str],
                                bar_width: float = 0.4, rotation: int = 0,
                                colormap: str = "viridis", group_spacing: float = 1.2, saving_name: str = 'multi_diagramm'):

    plt.rcParams.update(plt.rcParamsDefault)
    x = np.arange(len(df[x_column])) * group_spacing
    total_y_columns = len(y_columns)

    fig, ax = plt.subplots(figsize=(10, 5))

    cmap = plt.get_cmap(colormap)
    colors = [cmap(i / (total_y_columns - 1)) for i in range(total_y_columns)]

    for i, (y_col, color) in enumerate(zip(y_columns, colors)):
        ax.bar(x + (i - (total_y_columns - 1) / 2) * bar_width,
               df[y_col],
               bar_width,
               label=y_descriptions[i],
               color=color)

    ax.set_xticks(x)
    if rotation != 0:
        ax.set_xticklabels(df[x_column], rotation=rotation, ha='right', rotation_mode='anchor')
    else:
        ax.set_xticklabels(df[x_column])

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    ax.legend(loc='upper right', bbox_to_anchor=(1, 1))

    plt.savefig(f"{path_root}/Cloud-Telescope/data/diagramms/{saving_name}_bar_diagram.pdf", bbox_inches='tight')

    return plt


def port_multi_new_color_bar_diagram(
        df: pd.DataFrame, x_column: str, y_columns: list[str], x_label: str, y_label: str,
        y_descriptions: list[str], bar_width: float = 0.4, rotation: int = 0,
        custom_ticks_ax3: list[int] = None, custom_ticks_ax2: list[int] = None, custom_ticks_ax4: list[int] = None
):
    x = np.arange(len(df[x_column]))
    width = bar_width

    cmap = cm.get_cmap('viridis', len(y_columns))

    fig, ax1 = plt.subplots(figsize=(10, 5))

    ax2 = ax1.twinx()
    ax3 = ax1.twinx()
    ax4 = ax1.twinx()

    ax3.spines['right'].set_position(('outward', 60))
    ax4.spines['right'].set_position(('outward', 120))

    bars = []
    labels = []

    # Erste Spalte (ax1)
    bars.append(ax1.bar(x - 1.5 * width, df[y_columns[0]], width, color=cmap(0), alpha=0.7))
    labels.append(y_descriptions[0])
    ax1.set_ylabel(f'{y_descriptions[0]}', color=cmap(0))

    # Zweite Spalte (ax2)
    bars.append(ax2.bar(x - 0.5 * width, df[y_columns[1]], width, color=cmap(1), alpha=0.7))
    labels.append(y_descriptions[1])
    ax2.set_ylabel(f'{y_descriptions[1]}', color=cmap(1))

    # Dritte Spalte (ax3)
    bars.append(ax3.bar(x + 0.5 * width, df[y_columns[2]], width, color=cmap(2), alpha=0.7))
    labels.append(y_descriptions[2])
    ax3.set_ylabel(f'{y_descriptions[2]}', color=cmap(2))

    # Vierte Spalte (ax4)
    bars.append(ax4.bar(x + 1.5 * width, df[y_columns[3]], width, color=cmap(3), alpha=0.7))
    labels.append(y_descriptions[3])
    ax4.set_ylabel(f'{y_descriptions[3]}', color=cmap(3))
    ax4.set_yscale('symlog', linthresh=50)

    if custom_ticks_ax4 is not None:
        ax4.set_yticks(custom_ticks_ax4)
        ax4.set_yticklabels([str(tick) for tick in custom_ticks_ax4])

    ax3.set_yscale('symlog', linthresh=0.5)
    if custom_ticks_ax3 is not None:
        ax3.set_yticks(custom_ticks_ax3)

    ax2.set_yscale('symlog', linthresh=1000)
    if custom_ticks_ax2 is not None:
        ax2.set_yticks(custom_ticks_ax2)
        ax2.set_yticklabels([str(tick) for tick in custom_ticks_ax2])

    def custom_formatter(value, _):
        if value < 1:
            return f'{value:.1f}s'
        elif value < 60:
            return f'{int(value)}s'
        else:
            return f'{int(value // 60)}min'

    ax3.yaxis.set_major_formatter(FuncFormatter(custom_formatter))
    ax1.set_xticks(x)
    ax1.set_xticklabels(df[x_column], rotation=-rotation, ha='left', rotation_mode='anchor')
    fig.legend(bars, labels, loc='upper right', bbox_to_anchor=(0.82, 0.88), frameon=True)
    plt.savefig(f"{path_root}/Cloud-Telescope/data/diagramms/port_top20.pdf", bbox_inches='tight')
    return plt


def address_multi_new_3_color_bar_diagram(
        df: pd.DataFrame, x_column: str, y_columns: list[str], x_label: str, y_label: str,
        y_descriptions: list[str], bar_width: float = 0.4, rotation: int = 0,
        address_custom_ticks_ax2: list[int] = None, address_custom_ticks_ax4: list[int] = None,
        address_custom_ticks_ax3: list[int] = None
):
    x = np.arange(len(df[x_column]))
    width = bar_width

    fig, ax1 = plt.subplots(figsize=(10, 5))

    ax2 = ax1.twinx()
    ax3 = ax1.twinx()
    ax4 = ax1.twinx()

    ax3.spines['right'].set_position(('outward', 60))
    ax4.spines['right'].set_position(('outward', 120))

    cmap = cm.get_cmap('viridis', 4)
    colors = [cmap(i) for i in range(4)]

    bars = []
    labels = []

    # Erste Spalte (ax1)
    bars.append(ax1.bar(x - 1.5 * width, df[y_columns[0]], width, color=colors[0], alpha=0.7))
    labels.append(y_descriptions[0])
    ax1.set_ylabel(f'{y_descriptions[0]}', color=colors[0])

    # Zweite Spalte (ax2)
    bars.append(ax2.bar(x - 0.5 * width, df[y_columns[1]], width, color=colors[1], alpha=0.7))
    labels.append(y_descriptions[1])
    ax2.set_ylabel(f'{y_descriptions[1]}', color=colors[1])
    ax2.set_yscale('symlog', linthresh=10000)

    if address_custom_ticks_ax2 is not None:
        ax2.set_yticks(address_custom_ticks_ax2)
        ax2.set_yticklabels([str(tick) for tick in address_custom_ticks_ax2])

    # Dritte Spalte (ax3)
    bars.append(ax3.bar(x + 0.5 * width, df[y_columns[2]], width, color=colors[2], alpha=0.7))
    labels.append(y_descriptions[2])
    ax3.set_ylabel(f'{y_descriptions[2]}', color=colors[2])
    ax3.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f'{int(value // 60)}min'))

    if address_custom_ticks_ax3 is not None:
        ax3.set_yticks(address_custom_ticks_ax3)
        ax3.set_yticklabels([str(tick) for tick in address_custom_ticks_ax3])

    # Vierte Spalte (ax4)
    bars.append(ax4.bar(x + 1.5 * width, df[y_columns[3]], width, color=colors[3], alpha=0.7))
    labels.append(y_descriptions[3])
    ax4.set_ylabel(f'{y_descriptions[3]}', color=colors[3])
    ax4.set_yscale('symlog', linthresh=10)

    if address_custom_ticks_ax4 is not None:
        ax4.set_yticks(address_custom_ticks_ax4)
        ax4.set_yticklabels([str(tick) for tick in address_custom_ticks_ax4])

    ax1.set_xticks(x)
    ax1.set_xticklabels(df[x_column], rotation=-rotation, ha='left', rotation_mode='anchor')

    fig.legend(bars, labels, loc='upper right', bbox_to_anchor=(0.9, 0.88), frameon=True)
    plt.savefig(f"{path_root}/Cloud-Telescope/data/diagramms/address_top20.pdf", bbox_inches='tight')

    return plt


def stacked_three_bar_diagram(df: pd.DataFrame, x_column: str, y1_column: str, y2_column: str, y3_column: str, x_lable: str, y_lable: str, y1_description: str, y2_description: str, y3_description: str):
    fig, ax = plt.subplots(figsize=(10, 6))

    colors = ['#6b8e23', '#ffcc00', '#8b0000']

    df.set_index(x_column)[[y1_column, y2_column, y3_column]].plot(kind='bar', stacked=True, color=colors, ax=ax)

    ax.set_xlabel(x_lable)
    ax.set_ylabel(y_lable)

    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x)}' if x >= 1 else f'{x:.1f}'))

    ax.legend([y1_description, y2_description, y3_description])

    plt.xticks(rotation=45)

    plt.savefig(f"{path_root}/Cloud-Telescope/data/diagramms/scanning_types_bar_diagram.pdf", bbox_inches='tight')
    return plt


def plot_overlapping_bars(values_1, values_2, labels: list[str], saving_name: str, legend: bool, label_1='Säule 1', label_2='Säule 2', width=6, height=6, gap=1.0,
                          bar_width=0.4):
    x = np.array([0, 0 + gap])

    heights_1 = np.sort(values_1)[::-1]
    heights_2 = np.sort(values_2)[::-1]

    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']


    fig, ax = plt.subplots(figsize=(width, height))

    legend_handles = []
    for i in range(3):
        bar1 = ax.bar(x[0], heights_1[i], color=colors[i], alpha=0.5, width=bar_width)
        bar2 = ax.bar(x[1], heights_2[i], color=colors[i], alpha=0.5, width=bar_width)
        legend_handles.append((bar1[0], bar2[0]))

    ax.set_xticks(x)
    ax.set_xticklabels([label_1, label_2])
    ax.set_ylabel('Anzahl Scanner')

    if legend:
        ax.legend(legend_handles, labels, loc='upper right')
    else:
        ax.legend(legend_handles, labels, loc='upper left')
    plt.savefig(f"{path_root}/Cloud-Telescope/data/diagramms/{saving_name}_overlapped_bar.pdf", bbox_inches='tight')

    return plt


def plot_overlapping_two_bars(values_1, values_2, labels: list[str], saving_name: str, legend: bool, label_1='Säule 1',
                              label_2='Säule 2', width=6, height=6, gap=1.0,
                              bar_width=0.4):
    x = np.array([0, 0 + gap])

    heights_1 = np.sort(values_1)[::-1]
    heights_2 = np.sort(values_2)[::-1]

    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']

    fig, ax1 = plt.subplots(figsize=(width, height))
    ax2 = ax1.twinx()

    legend_handles = []
    for i in range(2):
        bar1 = ax1.bar(x[0], heights_1[i], color=colors[i], alpha=0.5, width=bar_width)
        bar2 = ax2.bar(x[1], heights_2[i], color=colors[i], alpha=0.5, width=bar_width)
        legend_handles.append((bar1[0], bar2[0]))

    ax1.set_xticks(x)
    ax1.set_xticklabels([label_1, label_2])
    ax1.set_ylabel('Anzahl Angriffe', color='black')
    ax2.set_ylabel('Anzahl Verbindungen', color='black')

    if legend:
        ax1.legend(legend_handles, labels, loc='upper right')
    else:
        ax1.legend(legend_handles, labels, loc='upper left')

    plt.savefig(f"{path_root}/Cloud-Telescope/data/diagramms/{saving_name}_bar.pdf", bbox_inches='tight')
    return plt
