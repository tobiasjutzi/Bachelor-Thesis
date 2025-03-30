import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import cm
from mpl_toolkits.axes_grid1 import make_axes_locatable
from src.d04_analysation.scanning import *
#from brokenaxes import brokenaxes
import matplotlib.transforms as mtransforms
from matplotlib.ticker import FuncFormatter


def seaborn_custom_bar_diagram(df: pd.DataFrame, x_column: str, y_column: str, x_lable: str, y_lable: str, rotation: int,
                        saving_name: str, diagram_width: int = 12, diagram_height: int = 6):
    plt.figure(figsize=(diagram_width, diagram_height))
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
