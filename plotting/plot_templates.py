from plotting.plot_utils import plot_df
from plotting.config import AxisConfig, CommonPlotConfig, PlotConfig
from metrics_extractor.metrics_io import load_metrics

import pandas as pd

def tps_players_plot(experiment, selected_metrics, type_exp):
    """
    Plot TPS and Players over time.
    :param experiment: The name of the experiment to plot.
    :param selected_metrics: List of selected metrics.
    :param type_exp: Type of experiment ('exp_vanilla' or 'exp_mod').
    """

    median_tps = load_metrics(selected_metrics[2], experiment, type_exp)
    quantile_95_tps = load_metrics(selected_metrics[3], experiment, type_exp)
    total_players = load_metrics(selected_metrics[4], experiment, type_exp)
    average_tps = load_metrics(selected_metrics[25], experiment, type_exp)

    primary_axis = AxisConfig(
        labels=["Median TPS", "95th Percentile TPS", "Average TPS"],
        ylabel="TPS",
        ylim=(0, 20),
        plot_kwargs=[
            {"color": "red", "linestyle": "-"},
            {"color": "blue", "linestyle": "-"},
            {"color": "orange", "linestyle": "-"}
        ]
    )

    secondary_axis = AxisConfig(
        labels=["Total Players"],
        ylabel="Players",
        ylim=(0, None),
        plot_kwargs=[
            {"color": "green", "linestyle": "-"}
        ]
    )


    common_conf = CommonPlotConfig(
        title="TPS and Players",
        figsize=(15, 6),
        show_legend=True,
        legend_kwargs={"loc": "upper left"},
        tight_layout=True,
        grid=True,
        grid_minor=False,
        minor_ticks=False,
        # grid_kwargs={"linestyle": "-"},
        # minor_grid_kwargs={"linestyle": ":"},
        time_unit='s',
        output_path=f"plots/{type_exp}/{experiment}/tps_players_{experiment}.pdf"
    )

    conf = PlotConfig(
        common=common_conf,
        primary_axis=primary_axis,
        secondary_axis=secondary_axis
    )

    #filter the data so that only timestamp and value are kept
    median_tps = median_tps[["timestamp", "value"]]
    quantile_95_tps = quantile_95_tps[["timestamp", "value"]]
    total_players = total_players[["timestamp", "value"]]
    average_tps = average_tps[["timestamp", "value"]]

    plot_df([median_tps, quantile_95_tps, average_tps], [total_players], conf)



def mspt_plot(experiment, selected_metrics, type_exp):
    """
    Plot MSPT (Mean Server Processing Time) per server.
    :param experiment: The name of the experiment to plot.
    :param selected_metrics: List of selected metrics.
    :param type_exp: Type of experiment ('exp_vanilla' or 'exp_mod').
    """
    
    mstp_data = load_metrics(selected_metrics[6], experiment, type_exp) # mc_mspt_seconds_10_mean

    servers = sorted(mstp_data["server_name"].unique())
    dfs_by_server = [
        mstp_data[mstp_data["server_name"] == server][["timestamp", "value"]].reset_index(drop=True)
        for server in servers
    ]

    primary_axis = AxisConfig(
        labels=[f"MSPT Server {i+1}" for i in range(len(servers))],
        ylabel="MSPT (ms)",
        # plot_kwargs=[
        #     {"color": "green", "linestyle": "-"},
        #     {"color": "red", "linestyle": "-"},
        #     {"color": "blue", "linestyle": "-"},
        # ]
        # ] + [{"color": f"C{i+1}", "linestyle": "-"} for i in range(len(servers))],

    )

    common_conf = CommonPlotConfig(
        title="MSPT per Server",
        figsize=(15, 6),
        show_legend=True,
        legend_kwargs={"loc": "upper left"},
        tight_layout=True,
        grid=True,
        grid_minor=False,
        minor_ticks=False,
        # grid_kwargs={"linestyle": "-"},
        # minor_grid_kwargs={"linestyle": ":"},
        time_unit='s',
        output_path=f"plots/{type_exp}/{experiment}/mspt_{experiment}.pdf"
    )

    conf = PlotConfig(
        common=common_conf,
        primary_axis=primary_axis,
    )

    plot_df(dfs_by_server, None, conf)  



def mspt_stats_plot(experiment, selected_metrics, type_exp):
    """
    Plot MSPT statistics: Average, Median, and 95th Percentile.
    :param experiment: The name of the experiment to plot.
    :param selected_metrics: List of selected metrics.
    :param type_exp: Type of experiment ('exp_vanilla' or 'exp_mod').
    """

    avg_mspt = load_metrics(selected_metrics[26], experiment, type_exp) # avg(mc_mspt_seconds_10_mean)
    quantile_95_mspt = load_metrics(selected_metrics[27], experiment, type_exp) # quantile(0.95, mc_mspt_seconds_10_mean)
    median_mspt = load_metrics(selected_metrics[28], experiment, type_exp) # quantile(0.5, mc_mspt_seconds_10_mean)

    primary_axis = AxisConfig(
        labels=["Median MSPT", "95th Percentile MSPT", "Average MSPT"],
        ylabel="MSPT",
        plot_kwargs=[
            {"color": "red", "linestyle": "-"},
            {"color": "blue", "linestyle": "-"},
            {"color": "orange", "linestyle": "-"}
        ]
    )

    # secondary_axis = AxisConfig(
    #     labels=["Total Players"],
    #     ylabel="Players",
    #     plot_kwargs=[
    #         {"color": "green", "linestyle": "-"}
    #     ]
    # )


    common_conf = CommonPlotConfig(
        title="MSPT (Average, Median, 95th Percentile)",
        figsize=(15, 6),
        show_legend=True,
        legend_kwargs={"loc": "upper left"},
        tight_layout=True,
        grid=True,
        grid_minor=False,
        minor_ticks=False,
        # grid_kwargs={"linestyle": "-"},
        # minor_grid_kwargs={"linestyle": ":"},
        time_unit='s',
        output_path=f"plots/{type_exp}/{experiment}/mspt_stats_{experiment}.pdf"
    )

    conf = PlotConfig(
        common=common_conf,
        primary_axis=primary_axis,
        # secondary_axis=secondary_axis
    )

    #filter the data so that only timestamp and value are kept
    avg_mspt = avg_mspt[["timestamp", "value"]]
    quantile_95_mspt = quantile_95_mspt[["timestamp", "value"]]
    median_mspt = median_mspt[["timestamp", "value"]]

    plot_df([avg_mspt, quantile_95_mspt, median_mspt], None, conf)




def player_tps_server_plot(experiment, selected_metrics, type_exp):
    """
    Plot Active Players and TPS per Server.
    :param experiment: The name of the experiment to plot.
    :param selected_metrics: List of selected metrics.
    :param type_exp: Type of experiment ('exp_vanilla' or 'exp_mod').
    """

    players_server = load_metrics(selected_metrics[0], experiment, type_exp) # mc_players_online_local
    server_tps = load_metrics(selected_metrics[1], experiment, type_exp) # mc_tps

    # Filter the players_server DataFrame to only include the relevant columns
    servers = sorted(players_server["server_name"].unique())
    # Create a DataFrame for each server's players
    dfs_by_server = [
        players_server[players_server["server_name"] == server][["timestamp", "value"]].reset_index(drop=True)
        for server in servers
    ]

    tps_server = server_tps[server_tps["server_name"].isin(servers)]
    # Create a DataFrame for each server's TPS
    dfs_by_server_tps = [
        tps_server[tps_server["server_name"] == server][["timestamp", "value"]].reset_index(drop=True)
        for server in servers
    ]

    primary_axis = AxisConfig(
        labels=[f"TPS Server {i+1}" for i in range(len(servers))],
        ylabel="TPS",
        ylim=(0, 20),
        plot_kwargs=[
            {"linestyle": "--"} for _ in servers
        ]
    )

    secondary_axis = AxisConfig(
        labels=[f"Players Server {i+1}" for i in range(len(servers))],
        ylabel="Active Players",
        ylim=(0, None),
        plot_kwargs=[
            {"linestyle": "-"} for _ in servers
        ]
    )

    common_conf = CommonPlotConfig(
        title="Active Players and TPS per Server",
        figsize=(15, 6),
        show_legend=True,
        legend_kwargs={"loc": "upper left"},
        tight_layout=True,
        grid=True,
        grid_minor=False,
        minor_ticks=False,
        # grid_kwargs={"linestyle": "-"},
        # minor_grid_kwargs={"linestyle": ":"},
        time_unit='s',
        output_path=f"plots/{type_exp}/{experiment}/player_tps_server_{experiment}.pdf"
    )

    conf = PlotConfig(
        common=common_conf,
        primary_axis=primary_axis,
        secondary_axis=secondary_axis
    )

    plot_df(dfs_by_server_tps, dfs_by_server, conf)  




def players_servers_plot(experiment, selected_metrics, type_exp):
    """
    Plot Active Players per Server.
    :param experiment: The name of the experiment to plot.
    :param selected_metrics: List of selected metrics.
    :param type_exp: Type of experiment ('exp_vanilla' or 'exp_mod').
    """

    players_server = load_metrics(selected_metrics[0], experiment, type_exp) # mc_players_online_local

    # Filter the players_server DataFrame to only include the relevant columns
    servers = sorted(players_server["server_name"].unique())
    # Create a DataFrame for each server's players
    dfs_by_server = [
        players_server[players_server["server_name"] == server][["timestamp", "value"]].reset_index(drop=True)
        for server in servers
    ]

    primary_axis = AxisConfig(
        labels=[f"Players Server {i+1}" for i in range(len(servers))],
        ylabel="Active Players",
        plot_kwargs=[
            {"linestyle": "-"} for _ in servers
        ]
    )

    common_conf = CommonPlotConfig(
        title="Active Players per Server",
        figsize=(15, 6),
        show_legend=True,
        legend_kwargs={"loc": "upper left"},
        tight_layout=True,
        grid=True,
        grid_minor=False,
        minor_ticks=False,
        # grid_kwargs={"linestyle": "-"},
        # minor_grid_kwargs={"linestyle": ":"},
        time_unit='s',
        output_path=f"plots/{type_exp}/{experiment}/players_server_{experiment}.pdf"
    )

    conf = PlotConfig(
        common=common_conf,
        primary_axis=primary_axis,
    )

    plot_df(dfs_by_server, None, conf)  



def tps_servers_plot(experiment, selected_metrics, type_exp):
    """
    Plot TPS per Server.
    :param experiment: The name of the experiment to plot.
    :param selected_metrics: List of selected metrics.
    :param type_exp: Type of experiment ('exp_vanilla' or 'exp_mod').
    """

    server_tps = load_metrics(selected_metrics[1], experiment, type_exp) # mc_tps

    servers = sorted(server_tps["server_name"].unique())
    # Create a DataFrame for each server's TPS
    dfs_by_server_tps = [
        server_tps[server_tps["server_name"] == server][["timestamp", "value"]].reset_index(drop=True)
        for server in servers
    ]


    primary_axis = AxisConfig(
        labels=[f"TPS Server {i+1}" for i in range(len(servers))],
        ylabel="TPS",
        ylim=(0, 20),
        plot_kwargs=[
            {"linestyle": "-"} for _ in servers
        ]
    )

    common_conf = CommonPlotConfig(
        title="TPS per Server",
        figsize=(15, 6),
        show_legend=True,
        legend_kwargs={"loc": "upper left"},
        tight_layout=True,
        grid=True,
        grid_minor=False,
        minor_ticks=False,
        # grid_kwargs={"linestyle": "-"},
        # minor_grid_kwargs={"linestyle": ":"},
        time_unit='s',
        output_path=f"plots/{type_exp}/{experiment}/tps_server_{experiment}.pdf"
    )

    conf = PlotConfig(
        common=common_conf,
        primary_axis=primary_axis,
    )

    plot_df(dfs_by_server_tps, None, conf)  



def chunk_ownership_plot(experiment, selected_metrics, type_exp):
    """
    Plot Chunk Ownership by Server.
    :param experiment: The name of the experiment to plot.
    :param selected_metrics: List of selected metrics.
    :param type_exp: Type of experiment ('exp_vanilla' or 'exp_mod').
    """

    chunk_ownership_by_owner = load_metrics(selected_metrics[15], experiment, type_exp)  # sum by(owner) (mc_chunk_ownership)

    servers = sorted(chunk_ownership_by_owner["owner"].unique())
    # Create a DataFrame for each server's players
    dfs_by_server = [
        chunk_ownership_by_owner[chunk_ownership_by_owner["owner"] == server][["timestamp", "value"]].reset_index(drop=True)
        for server in servers
    ]

    primary_axis = AxisConfig(
        labels=[f"Chunks Server {i+1}" for i in range(len(servers))],
        ylabel="Chunks Owned",
        plot_kwargs=[
            {"linestyle": "-"} for _ in servers
        ]
    )

    common_conf = CommonPlotConfig(
        title="Chunk Ownership by Server",
        figsize=(15, 6),
        show_legend=True,
        legend_kwargs={"loc": "best"},
        tight_layout=True,
        grid=True,
        grid_minor=False,
        minor_ticks=False,
        time_unit='s',
        output_path=f"plots/{type_exp}/{experiment}/chunk_ownership_{experiment}.pdf"
    )

    conf = PlotConfig(
        common=common_conf,
        primary_axis=primary_axis,
    )

    plot_df(dfs_by_server, None, conf)



def players_chunks_owner_plot(experiment, selected_metrics, type_exp):
    """
    Plot Chunk Ownership by Player.
    :param experiment: The name of the experiment to plot.
    :param selected_metrics: List of selected metrics.
    :param type_exp: Type of experiment ('exp_vanilla' or 'exp_mod').
    """
    
    players_chunks = load_metrics(selected_metrics[18], experiment, type_exp) # sum by(chunk_owner) (mc_player_location)

    servers = sorted(players_chunks["chunk_owner"].dropna().astype(str).unique())
    # Create a DataFrame for each server's players
    dfs_by_server = [
        players_chunks[players_chunks["chunk_owner"] == server][["timestamp", "value"]].reset_index(drop=True)
        for server in servers
    ]

    primary_axis = AxisConfig(
        labels=[f"Chunks Server {i+1}" for i in range(len(servers))],
        ylabel="Num Players",
        plot_kwargs=[
            {"linestyle": "-"} for _ in servers
        ]
    )

    common_conf = CommonPlotConfig(
        title="Nº Players in Chunks owned by Server",
        figsize=(15, 6),
        show_legend=True,
        legend_kwargs={"loc": "best"},
        tight_layout=True,
        grid=True,
        grid_minor=False,
        minor_ticks=False,
        time_unit='s',
        output_path=f"plots/{type_exp}/{experiment}/num_players_chunk{experiment}.pdf"
    )

    conf = PlotConfig(
        common=common_conf,
        primary_axis=primary_axis,
    )

    plot_df(dfs_by_server, None, conf)

def quality_master_plot(experiment, selected_metrics, type_exp, band):
    """
    Plot Quality ratio per server.
    :param experiment: The name of the experiment to plot.
    :param selected_metrics: List of selected metrics.
    :param type_exp: Type of experiment ('exp_vanilla' or 'exp_mod').
    """
    
    quality = load_metrics(selected_metrics[32], experiment, type_exp) # (veloctiy_server_quality)

    servers = sorted(quality["exported_server_name"].dropna().astype(str).unique())

    dfs_by_server = [
        quality[quality["exported_server_name"] == server][["timestamp", "value"]].reset_index(drop=True)
        for server in servers
    ]

    primary_axis = AxisConfig(
        labels=[f"Server {i+1}" for i in range(len(servers))],
        ylabel="Quality",
        plot_kwargs=[
            {"linestyle": "-"} for _ in servers
        ]
    )

    common_conf = CommonPlotConfig(
        title="Quality ratio by Server",
        figsize=(15, 6),
        show_legend=True,
        legend_kwargs={"loc": "best"},
        tight_layout=True,
        grid=True,
        grid_minor=False,
        minor_ticks=False,
        band = band,
        time_unit='s',
        output_path=f"plots/{type_exp}/{experiment}/quality_{experiment}.pdf"
    )

    conf = PlotConfig(
        common=common_conf,
        primary_axis=primary_axis,
    )

    plot_df(dfs_by_server, None, conf)

def players_master_plot(experiment, selected_metrics, type_exp):
    """
    Plot Quality ratio per server.
    :param experiment: The name of the experiment to plot.
    :param selected_metrics: List of selected metrics.
    :param type_exp: Type of experiment ('exp_vanilla' or 'exp_mod').
    """
    
    players = load_metrics(selected_metrics[31], experiment, type_exp) # (veloctiy_server_players)

    servers = sorted(players["exported_server_name"].dropna().astype(str).unique())

    dfs_by_server = [
        players[players["exported_server_name"] == server][["timestamp", "value"]].reset_index(drop=True)
        for server in servers
    ]

    primary_axis = AxisConfig(
        labels=[f"Server {i+1}" for i in range(len(servers))],
        ylabel="Players",
        plot_kwargs=[
            {"linestyle": "-"} for _ in servers
        ]
    )

    common_conf = CommonPlotConfig(
        title="Num. players by Server",
        figsize=(15, 6),
        show_legend=True,
        legend_kwargs={"loc": "best"},
        tight_layout=True,
        grid=True,
        grid_minor=False,
        minor_ticks=False,
        time_unit='s',
        output_path=f"plots/{type_exp}/{experiment}/players_{experiment}.pdf"
    )

    conf = PlotConfig(
        common=common_conf,
        primary_axis=primary_axis,
    )

    plot_df(dfs_by_server, None, conf)

def mspt_master_plot(experiment, selected_metrics, type_exp):
    """
    Plot Quality ratio per server.
    :param experiment: The name of the experiment to plot.
    :param selected_metrics: List of selected metrics.
    :param type_exp: Type of experiment ('exp_vanilla' or 'exp_mod').
    """
    
    mspt = load_metrics(selected_metrics[30], experiment, type_exp) # (veloctiy_server_players)

    servers = sorted(mspt["exported_server_name"].dropna().astype(str).unique())

    dfs_by_server = [
        mspt[mspt["exported_server_name"] == server][["timestamp", "value"]].reset_index(drop=True)
        for server in servers
    ]

    primary_axis = AxisConfig(
        labels=[f"Server {i+1}" for i in range(len(servers))],
        ylabel="MSPT",
        plot_kwargs=[
            {"linestyle": "-"} for _ in servers
        ]
    )

    common_conf = CommonPlotConfig(
        title="MSPT by Server",
        figsize=(15, 6),
        show_legend=True,
        legend_kwargs={"loc": "best"},
        tight_layout=True,
        grid=True,
        grid_minor=False,
        minor_ticks=False,
        time_unit='s',
        output_path=f"plots/{type_exp}/{experiment}/mspt_{experiment}.pdf"
    )

    conf = PlotConfig(
        common=common_conf,
        primary_axis=primary_axis,
    )

    plot_df(dfs_by_server, None, conf)

def mspt_tps_master_plot(experiment, selected_metrics, type_exp):
    """
    Plot MSPT and TPS.
    :param experiment: The name of the experiment to plot.
    :param selected_metrics: List of selected metrics.
    :param type_exp: Type of experiment ('exp_vanilla' or 'exp_mod').
    """

    mspt = load_metrics(selected_metrics[30], experiment, type_exp) # (veloctiy_server_players)
    average_tps = load_metrics(selected_metrics[25], experiment, type_exp)

    # primary_axis = AxisConfig(
    #     labels=["MSPT"],
    #     ylabel="MSPT",
    #     ylim=(0, None),
    #     plot_kwargs=[
    #         {"color": "blue", "linestyle": "-"}
    #     ]
    # )

    servers = sorted(mspt["exported_server_name"].dropna().astype(str).unique())
    dfs_by_server = [
        mspt[mspt["exported_server_name"] == server][["timestamp", "value"]].reset_index(drop=True)
        for server in servers
    ]

    primary_axis = AxisConfig(
        labels=[f"Server {i+1}" for i in range(len(servers))],
        ylabel="MSPT",
        plot_kwargs=[
            {"linestyle": "-"} for _ in servers
        ]
    )

    secondary_axis = AxisConfig(
        labels=["Average TPS"],
        ylabel="Avg TPS",
        ylim=(0, 20),
        plot_kwargs=[
            {"color": "orange", "linestyle": "-"}
        ]
    )

    common_conf = CommonPlotConfig(
        title="MSPT and avg TPS",
        figsize=(15, 6),
        show_legend=True,
        legend_kwargs={"loc": "upper left"},
        tight_layout=True,
        grid=True,
        grid_minor=False,
        minor_ticks=False,
        # grid_kwargs={"linestyle": "-"},
        # minor_grid_kwargs={"linestyle": ":"},
        time_unit='s',
        output_path=f"plots/{type_exp}/{experiment}/mspt_tps_{experiment}.pdf"
    )

    conf = PlotConfig(
        common=common_conf,
        primary_axis=primary_axis,
        secondary_axis=secondary_axis
    )

    #filter the data so that only timestamp and value are kept
    average_tps = average_tps[["timestamp", "value"]]

    plot_df( dfs_by_server, [average_tps], conf)

def owned_chunks_master_plot(experiment, selected_metrics, type_exp):
    """
    Plot Chunk Ownership by Server.
    :param experiment: The name of the experiment to plot.
    :param selected_metrics: List of selected metrics.
    :param type_exp: Type of experiment ('exp_vanilla' or 'exp_mod').
    """

    chunks = load_metrics(selected_metrics[29], experiment, type_exp) # (veloctiy_server_chunks)

    servers = sorted(chunks["exported_server_name"].unique())
    # Create a DataFrame for each server's players
    dfs_by_server = [
        chunks[chunks["exported_server_name"] == server][["timestamp", "value"]].reset_index(drop=True)
        for server in servers
    ]

    # Calcular el màxim i el mínim de la diferència del nombre de chunks entre servers
    combined_df = pd.concat(
        [df.set_index("timestamp")["value"].rename(f"server_{i+1}") for i, df in enumerate(dfs_by_server)],
        axis=1
    )
    # Calculate max-min difference
    max_min_diff = abs(combined_df.max(axis=1) - combined_df.min(axis=1))
    # Create a DataFrame for the difference
    diff_df = pd.DataFrame({"timestamp": max_min_diff.index, "value": max_min_diff.values}).reset_index(drop=True)

    # Cal ajustar els zeros de les escales del gràfic al mateix nivell
    primary_max = max(df["value"].max() for df in dfs_by_server)
    primary_min = min(df["value"].min() for df in dfs_by_server)
    primary_ylim = (min(0, primary_min), primary_max * 1.1)

    # Calcular els límits per al secondary_axis
    secondary_max = diff_df["value"].max()
    secondary_min = 0
    secondary_ylim = (secondary_min, secondary_max * 1.1)

    primary_axis = AxisConfig(
        labels=[f"Chunks Server {i+1}" for i in range(len(servers))],
        ylabel="Chunks Owned",
        ylim = primary_ylim,
        plot_kwargs=[
            {"linestyle": "-"} for _ in servers
        ]
    )

    secondary_axis = AxisConfig(
        labels=["Max. difference of owned chunks between all servers"],
        ylabel="Chunks",
        ylim=secondary_ylim,
        plot_kwargs=[
            {"color": "black", "linestyle": "dashdot"}
        ]
    )

    common_conf = CommonPlotConfig(
        title="Owned Chunks by Server",
        figsize=(15, 6),
        show_legend=True,
        legend_kwargs={"loc": "best"},
        tight_layout=True,
        grid=True,
        grid_minor=False,
        minor_ticks=False,
        time_unit='s',
        output_path=f"plots/{type_exp}/{experiment}/chunk_ownership_{experiment}.pdf"
    )

    conf = PlotConfig(
        common=common_conf,
        primary_axis=primary_axis,
        secondary_axis=secondary_axis
    )

    plot_df(dfs_by_server, [diff_df], conf)

def max_diff_chunks_master_plot(experiment, selected_metrics, type_exp):
    """
    Plot Chunk Ownership by Server.
    :param experiment: The name of the experiment to plot.
    :param selected_metrics: List of selected metrics.
    :param type_exp: Type of experiment ('exp_vanilla' or 'exp_mod').
    """

    chunks = load_metrics(selected_metrics[29], experiment, type_exp) # (veloctiy_server_chunks)

    servers = sorted(chunks["exported_server_name"].unique())
    # Create a DataFrame for each server's players
    dfs_by_server = [
        chunks[chunks["exported_server_name"] == server][["timestamp", "value"]].reset_index(drop=True)
        for server in servers
    ]

    # Calcular el màxim i el mínim de la diferència del nombre de chunks entre servers
    combined_df = pd.concat(
        [df.set_index("timestamp")["value"].rename(f"server_{i+1}") for i, df in enumerate(dfs_by_server)],
        axis=1
    )
    # Calculate max-min difference
    max_min_diff = abs(combined_df.max(axis=1) - combined_df.min(axis=1))
    # Create a DataFrame for the difference
    diff_df = pd.DataFrame({"timestamp": max_min_diff.index, "value": max_min_diff.values}).reset_index(drop=True)

    primary_axis = AxisConfig(
        labels=[f"Chunks Server {i+1}" for i in range(len(servers))],
        ylabel="Chunks Owned",
        plot_kwargs=[
            {"color": "black"} for _ in servers
        ]
    )

    common_conf = CommonPlotConfig(
        title="Max. difference of owned chunks by server",
        figsize=(15, 6),
        show_legend=True,
        legend_kwargs={"loc": "best"},
        tight_layout=True,
        grid=True,
        grid_minor=False,
        minor_ticks=False,
        time_unit='s',
        output_path=f"plots/{type_exp}/{experiment}/chunk_diff_{experiment}.pdf"
    )

    conf = PlotConfig(
        common=common_conf,
        primary_axis=primary_axis,
    )

    plot_df([diff_df], None, conf)