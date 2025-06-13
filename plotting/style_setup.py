import matplotlib as mpl
import matplotlib.pyplot as plt
from cycler import cycler


def setup_plot_style():
    """
    Set up the matplotlib style for plots.
    This function configures the global matplotlib settings to ensure consistent styling across plots.
    """

    # mpl.use("pdf")
    # plt.close("all")
    plt.rcParams.update(
        {
            "text.usetex": True,
            "font.family": "serif",
            "pgf.texsystem": "pdflatex",
            "font.size": 12,  # footnote/caption size 9pt for paper
            # "font.size": 10,     # caption size 10pt on thesis
            "pgf.preamble": "\n".join(
                [
                    r"\usepackage{libertine}",
                    # r"\usepackage{lmodern}",
                ]
            ),
            # "lines.linewidth": 0.8,
            "lines.markersize": 3,
            "axes.linewidth": 0.5,
            "grid.linewidth": 0.3,
            "grid.linestyle": "-",
            "axes.edgecolor": mpl.rcParams["grid.color"],
            # "ytick.color": mpl.rcParams["grid.color"],
            "ytick.direction": "in",
            # "xtick.color": mpl.rcParams["grid.color"],
            "xtick.direction": "in",
            "axes.titlesize": "medium",
            "axes.titlepad": 4,
            "axes.labelpad": 1,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.spines.bottom": False,
            "axes.spines.left": False,
            "axes.axisbelow": True,  # grid below patches
            "axes.prop_cycle": cycler(
                "color", ["#348ABD", "#7A68A6", "#A60628", "#467821", "#CF4457", "#188487", "#E24A33"]
            ),
            "legend.labelspacing": 0.1,
            "legend.handlelength": 1,
            "legend.handletextpad": 0.2,
            "legend.columnspacing": 1,
            "legend.borderpad": 0.1,
        }
    )
