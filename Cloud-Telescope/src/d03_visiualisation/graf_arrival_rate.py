import pandas as pd
import matplotlib.dates as mdates
import numpy as np
import matplotlib.pyplot as plt
import itertools
from matplotlib.ticker import LogFormatter
from src.config import *


def multi_arrival_rate_days(dfs: list[pd.DataFrame], df_colors: list[str], df_descriptions: list[str], x_description: str, y_description: str, y_ticks: list[int], linthresh: int = 0, grade: str = '', saving_name: str = 'graf'):

    fig, ax = plt.subplots(figsize=(16, 6))

    start_time = pd.Timestamp("2025-01-21 16:00:00", tz="UTC")
    dfs = [df[df["timestamp"] >= start_time] for df in dfs]

    first_df = dfs[0]
    buffer = (first_df["timestamp"].max() - start_time) * 0.01  # 4% Abstand
    ax.set_xlim(start_time - buffer, first_df["timestamp"].max() + buffer)

    for i, df in enumerate(dfs, start=1):

        dummy_left = pd.DataFrame({"timestamp": [start_time - buffer], "total_count": [np.nan]})
        dummy_right = pd.DataFrame({"timestamp": [first_df["timestamp"].max() + buffer], "total_count": [np.nan]})

        df = pd.concat([dummy_left, df, dummy_right])

        ax.plot(df['timestamp'], df['total_count'], linestyle='-', color=df_colors[i - 1], linewidth=0.5, label=df_descriptions[i - 1])

    ax.set_xlabel(x_description, fontsize=12)
    ax.set_ylabel(y_description, fontsize=12)
    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d'))
    ax.tick_params(axis='x', rotation=0, labelsize=10)
    ax.tick_params(axis='y', labelsize=10)

    ax.margins(x=0.04, y=0.02)

    if grade != '':
        if grade != '' and linthresh != 0:
            ax.set_yscale(grade, linthresh=linthresh)
        else:
            ax.set_yscale(grade)

    if len(y_ticks) > 0:
        ax.set_yticks(y_ticks)
        ax.get_yaxis().set_major_formatter(plt.ScalarFormatter())

    ax.legend()

    ax.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()

    plt.savefig(f"{path_root}/Cloud-Telescope/data/diagramms/{saving_name}_arrival_rate.pdf", bbox_inches='tight')

    return plt

