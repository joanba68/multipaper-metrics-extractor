import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from typing import Optional, List
from plotting.config import PlotConfig, AxisConfig, CommonPlotConfig

def plot_df(
    primary_dfs: List[pd.DataFrame],
    secondary_dfs: Optional[List[pd.DataFrame]],
    plot_config: PlotConfig
):
    # Extract configurations from plot_config
    common = plot_config.common
    primary_axis = plot_config.primary_axis
    secondary_axis = plot_config.secondary_axis
    title = common.title
    time_unit = common.time_unit
    show_legend = common.show_legend
    grid = common.grid
    grid_minor = common.grid_minor
    tight_layout = common.tight_layout

    # Calculate the minimum timestamp for alignment
    min_time = min(
        [df['timestamp'].min() for df in primary_dfs + (secondary_dfs or [])]
    )

    # Plotting
    fig, ax1 = plt.subplots(figsize=common.figsize)

    # Plot primary y-axis data
    for i, df in enumerate(primary_dfs):
        df['time_since_start'] = (df['timestamp'] - min_time).dt.total_seconds()
        plot_kwargs = primary_axis.plot_kwargs[i] if i < len(primary_axis.plot_kwargs) else {}
        ax1.plot(
            df['time_since_start'], df['value'], 
            label=primary_axis.labels[i] if primary_axis.labels else None,
            **plot_kwargs  # Apply unique styling options per time series
        )

    # Configure secondary y-axis if provided
    if secondary_axis and secondary_dfs:
        ax2 = ax1.twinx()
        for i, df in enumerate(secondary_dfs):
            df['time_since_start'] = (df['timestamp'] - min_time).dt.total_seconds()
            plot_kwargs = secondary_axis.plot_kwargs[i] if i < len(secondary_axis.plot_kwargs) else {}
            ax2.plot(
                df['time_since_start'], df['value'],
                label=secondary_axis.labels[i] if secondary_axis.labels else None,
                **plot_kwargs  # Apply unique styling options per time series on the secondary axis
            )
        ax2.set_ylabel(secondary_axis.ylabel)
        if secondary_axis.ylim:
            ax2.set_ylim(secondary_axis.ylim)
        
    # Set axis labels and limits
    ax1.set_xlabel(f"Time ({time_unit})")
    ax1.set_ylabel(primary_axis.ylabel)
    if primary_axis.ylim:
        ax1.set_ylim(primary_axis.ylim)
    if common.xlim:
        ax1.set_xlim(common.xlim)
        if secondary_axis and secondary_dfs:
            ax2.set_xlim(common.xlim)

    # Plot title and legends
    plt.title(title)
    if show_legend:
        lines_primary, labels_primary = ax1.get_legend_handles_labels()
        if secondary_axis and secondary_dfs:
            lines_secondary, labels_secondary = ax2.get_legend_handles_labels()
            ax1.legend(lines_primary + lines_secondary, labels_primary + labels_secondary, **common.legend_kwargs)
        else:
            ax1.legend(lines_primary, labels_primary, **common.legend_kwargs)

    # Grid and layout options
    if common.minor_ticks:
        ax1.minorticks_on()
        if secondary_axis and secondary_dfs:
            ax2.minorticks_on()
    if grid:
        ax1.grid(visible=True, which='both', axis='both', **common.grid_kwargs)
    if grid_minor:
        ax1.grid(visible=True, which='minor', axis='both', **common.minor_grid_kwargs)

    if secondary_axis and secondary_dfs:
        # Align the secondary y-axis with the primary y-axis
        ax2.set_yticks(np.linspace(ax2.get_yticks()[0], ax2.get_yticks()[-1], len(ax1.get_yticks())))
    
    if tight_layout:
        plt.tight_layout()
    if common.subplots_adjust:
        plt.subplots_adjust(**common.subplots_adjust)

    if common.output_path:
        output_dir = os.path.dirname(common.output_path)
        os.makedirs(output_dir, exist_ok=True)
        plt.savefig(common.output_path, format='pdf', bbox_inches='tight')

    plt.show()
