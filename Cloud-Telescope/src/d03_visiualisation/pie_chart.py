import matplotlib.pyplot as plt
import pandas as pd
from src.config import *


def plot_pie_chart(df, value_column: str, label_column: str, saving_name: str):
    values = df[value_column]
    labels = df[label_column]

    plt.figure(figsize=(6, 6))
    plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140, colors=['blueviolet', 'green', 'coral', 'darkslategray', 'burlywood', 'dimgrey'])
    plt.savefig(f"{path_root}/Cloud-Telescope/data/diagramms/{saving_name}_pie_chart.pdf", bbox_inches='tight')

    return plt


def plot_pie_transport_protocol(df, value_column: str, label_column: str, saving_name: str):
    values = df[value_column]

    plt.figure(figsize=(6, 6))
    plt.pie(
        values,
        labels=None,
        autopct=None,
        startangle=140,
        colors=['blueviolet', 'green', 'coral', 'darkslategray', 'burlywood', 'dimgrey', 'lime']
    )
    plt.savefig(f"{path_root}/Cloud-Telescope/data/diagramms/{saving_name}_pie_chart.pdf", bbox_inches='tight')

    return plt


def autopct_format(pct):
    return ('%1.1f%%' % pct) if pct > 2 else ''


def filter_labels(labels, values):
    total = sum(values)
    return [label if (value / total) * 100 > 2 else '' for label, value in zip(labels, values)]


def plot_pie_application_protocol(df, value_column: str, label_column: str, saving_name: str):
    values = df[value_column]
    labels = filter_labels(df[label_column], values)

    plt.figure(figsize=(6, 6))
    plt.pie(values, labels=labels, autopct=lambda pct: autopct_format(pct), startangle=140, colors=['lightblue', 'lightgreen', 'lightcoral'])
    plt.savefig(f"{path_root}/Cloud-Telescope/data/diagramms/{saving_name}_pie_chart.pdf", bbox_inches='tight')

    return plt