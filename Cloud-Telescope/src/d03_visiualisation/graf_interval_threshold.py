import pandas as pd
import matplotlib.pyplot as plt
from src.config import *


def graf_new_interval_threshold(dataframes: list[pd.DataFrame], df_labels: list[str], df_linestyle: list[str], df_marker: list[str], x_label: str, y_label: str, saving_name: str):
    plt.figure(figsize=(10, 5))
    x_values = dataframes[0]["interval"] // 60

    for index, df in enumerate(dataframes):
        y_values = df.set_index("interval").reindex(dataframes[0]["interval"])["scaled_scanner"]  # Reindex auf erste X-Werte
        plt.plot(x_values, y_values, label=df_labels[index], linestyle=df_linestyle[index], marker=df_marker[index])

    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.xticks(x_values)
    plt.legend()
    plt.grid(True)

    plt.savefig(f"{path_root}/Cloud-Telescope/data/diagramms/{saving_name}_graf_multi.pdf", bbox_inches='tight')
    return plt
