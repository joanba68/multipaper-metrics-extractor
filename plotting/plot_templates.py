from plotting.plot_utils import plot_df
from plotting.config import AxisConfig, CommonPlotConfig, PlotConfig
from metrics_extractor.metrics_io import load_metrics


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