import pandas as pd
import os

def load_metrics(selected_metric, experiment, type_exp):
    metric_name = selected_metric.split("{")[0]  # Get the base metric name without filters
    if "master" in selected_metric:
        metric_name = f"{metric_name}_master"
    elif "server" in selected_metric:
        metric_name = f"{metric_name}_server"
    df = pd.read_csv(f"metrics/{type_exp}/{experiment}/{metric_name}.csv")
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df


def save_metrics(selected_metrics, from_time, to_time, source, extractor, experiment, type_exp):
    metrics_data = extractor.extract(
        source=source,
        metrics=selected_metrics,
        from_time=from_time,
        to_time=to_time,
        output_format="pandas",
    )
    # create the directory if it does not exist
    output_dir = f"metrics/{type_exp}/{experiment}"
    os.makedirs(output_dir, exist_ok=True)
    # save the data to a file
    for metric_name, data in metrics_data.items():
        # only get the name of the metric, remove the filter part or the function part
        base_metric_name = metric_name.split("{")[0]
        # add a suffix to the metric name
        suffix = ""
        if "master" in metric_name:
            suffix = "_master"
        elif "server" in metric_name:
            suffix = "_server"

        data.to_csv(f"metrics/{type_exp}/{experiment}/{base_metric_name}{suffix}.csv")
