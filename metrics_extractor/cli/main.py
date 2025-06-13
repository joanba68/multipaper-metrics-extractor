"""
Command-line interface for the Metrics Extractor.
"""

import logging
import os
import traceback
from datetime import datetime
from typing import Optional, Dict, Any, Union

import click
import pandas as pd
import requests
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from metrics_extractor import InfluxDBSource, MetricsExtractor, PrometheusSource
from metrics_extractor.core.datasource import DataSource
from metrics_extractor.core.logging import logger

# Create console for rich output
console = Console()


@click.group()
@click.version_option()
def cli():
    """Extract metrics from Prometheus and InfluxDB."""


@cli.command()
@click.option(
    "--source",
    type=click.Choice(["prometheus", "influxdb"]),
    required=True,
    help="Data source to extract metrics from",
)
@click.option("--url", required=True, help="URL of the data source")
@click.option(
    "--metrics",
    help="Comma-separated list of metrics to extract",
)
@click.option(
    "--all-metrics",
    is_flag=True,
    help="Extract all available metrics",
)
@click.option(
    "--from",
    "from_time",
    help="Start time for extraction (ISO 8601 format, e.g., '2023-01-01T00:00:00Z')",
)
@click.option(
    "--to",
    "to_time",
    help="End time for extraction (ISO 8601 format, e.g., '2023-01-02T00:00:00Z')",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["pandas", "csv", "json", "parquet", "hdf5", "feather"]),
    default="csv",
    help="Output format for the extracted data",
)
@click.option(
    "--output-file",
    required=True,
    help="Path to save the extracted data. For multiple metrics, this will be used as a base for the filename (e.g. 'metrics.csv' becomes 'metrics_metric_name.csv')",
)
@click.option(
    "--token",
    help="API token for InfluxDB",
)
@click.option(
    "--org",
    help="Organization for InfluxDB",
)
@click.option(
    "--bucket",
    help="Bucket for InfluxDB",
)
@click.option(
    "--parallel",
    is_flag=True,
    help="Extract metrics in parallel",
)
@click.option(
    "--max-workers",
    type=int,
    default=4,
    help="Maximum number of parallel workers",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output",
)
@click.option(
    "--combined-output",
    is_flag=True,
    help="Combine all metrics into a single output file (legacy behavior)",
)
def extract(
    source: str,
    url: str,
    metrics: Optional[str],
    all_metrics: bool,
    from_time: Optional[str],
    to_time: Optional[str],
    output_format: str,
    output_file: str,
    token: Optional[str],
    org: Optional[str],
    bucket: Optional[str],
    parallel: bool,
    max_workers: int,
    verbose: bool,
    combined_output: bool,
):
    """
    Extract metrics from the specified data source.

    Examples:

    \b
    # Extract metrics from Prometheus (each metric to a separate file)
    metrics-extractor extract --source prometheus --url http://prometheus:9090 \\
        --metrics "http_requests_total,node_cpu_seconds_total" \\
        --from "2023-01-01T00:00:00Z" --to "2023-01-02T00:00:00Z" \\
        --format parquet --output-file ./metrics.parquet

    \b
    # Extract metrics from Prometheus to a single file (legacy behavior)
    metrics-extractor extract --source prometheus --url http://prometheus:9090 \\
        --metrics "http_requests_total,node_cpu_seconds_total" \\
        --from "2023-01-01T00:00:00Z" --to "2023-01-02T00:00:00Z" \\
        --format parquet --output-file ./metrics.parquet --combined-output

    \b
    # Extract all metrics from InfluxDB
    metrics-extractor extract --source influxdb --url http://influxdb:8086 \\
        --token my-token --org my-org --bucket prometheus \\
        --all-metrics --format hdf5 --output-file ./all_metrics.h5
    """
    # Set logging level
    if verbose:
        logger.setLevel(logging.DEBUG)

    # Parse metrics
    metrics_list = None
    if metrics:
        metrics_list = [m.strip() for m in metrics.split(",")]
    elif not all_metrics:
        console.print(
            "[bold red]Error:[/bold red] Either --metrics or --all-metrics must be specified"
        )
        return

    # Parse time range
    from_datetime = None
    to_datetime = None

    if from_time:
        try:
            from_datetime = datetime.fromisoformat(from_time.replace("Z", "+00:00"))
        except ValueError:
            console.print(f"[bold red]Error:[/bold red] Invalid from time format: {from_time}")
            return

    if to_time:
        try:
            to_datetime = datetime.fromisoformat(to_time.replace("Z", "+00:00"))
        except ValueError:
            console.print(f"[bold red]Error:[/bold red] Invalid to time format: {to_time}")
            return

    # Create the appropriate data source
    data_source: Optional[DataSource] = None
    try:
        if source == "prometheus":
            console.print("Connecting to Prometheus...")
            data_source = PrometheusSource(url=url)
        elif source == "influxdb":
            if not token or not org or not bucket:
                console.print(
                    "[bold red]Error:[/bold red] --token, --org, and --bucket are required for InfluxDB"
                )
                return

            console.print("Connecting to InfluxDB...")
            data_source = InfluxDBSource(
                url=url,
                token=token,
                org=org,
                bucket=bucket,
            )
    except (ConnectionError, ValueError, IOError) as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        if verbose:
            console.print(traceback.format_exc())
        return

    # Ensure we have a valid data source
    if data_source is None:
        console.print("[bold red]Error:[/bold red] Failed to initialize data source")
        return

    # Create extractor
    extractor = MetricsExtractor()

    try:
        # Extract data
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task_id = progress.add_task(
                description="Extracting metrics...",
                total=None,
            )

            if parallel and metrics_list and len(metrics_list) > 1:
                console.print(f"Extracting {len(metrics_list)} metrics in parallel...")
                data = extractor.extract_parallel(
                    source=data_source,
                    metrics=metrics_list,
                    from_time=from_datetime,
                    to_time=to_datetime,
                    output_format=output_format,
                    max_workers=max_workers,
                    separate_metrics=not combined_output,
                )
            else:
                console.print("Extracting metrics...")
                data = extractor.extract(
                    source=data_source,
                    metrics=metrics_list,
                    from_time=from_datetime,
                    to_time=to_datetime,
                    output_format=output_format,
                    separate_metrics=not combined_output,
                )

            progress.update(task_id, completed=True)

        # If we have combined output, save to a single file
        if combined_output or not isinstance(data, dict):
            # Combined output or single metric
            console.print(f"Saving data to {output_file}...")
            
            if output_format == "pandas" and isinstance(data, pd.DataFrame):
                # For pandas format, we need to save the DataFrame
                if output_file.endswith(".csv"):
                    data.to_csv(output_file)
                elif output_file.endswith(".parquet"):
                    data.to_parquet(output_file)
                elif output_file.endswith(".h5") or output_file.endswith(".hdf5"):
                    data.to_hdf(output_file, key="metrics")
                elif output_file.endswith(".json"):
                    data.to_json(output_file, orient="records")
                elif output_file.endswith(".feather"):
                    data.to_feather(output_file)
                else:
                    # Default to CSV
                    data.to_csv(output_file)
            else:
                # For other formats, save the already formatted data
                with open(output_file, "wb" if isinstance(data, bytes) else "w") as f:
                    f.write(data)

            console.print(f"[bold green]Success![/bold green] Data saved to {output_file}")

            # Print summary for pandas data
            if isinstance(data, pd.DataFrame):
                console.print(f"[bold]Summary:[/bold] {len(data)} rows, {len(data.columns)} columns")
        else:
            # We have multiple metrics to save to separate files
            assert isinstance(data, dict), "Expected a dictionary of metrics when not using combined output"
            console.print(f"Saving metrics to separate files...")
            
            # Get base file name and extension
            base_name, extension = os.path.splitext(output_file)
            
            # Track total files saved for summary
            files_saved = 0
            
            # Process each metric
            for metric_name, metric_data in data.items():
                # Generate unique filename for each metric
                metric_file = f"{base_name}_{metric_name}{extension}"
                console.print(f"Saving metric '{metric_name}' to {metric_file}...")
                
                if output_format == "pandas" and isinstance(metric_data, pd.DataFrame):
                    # For pandas format, we need to save the DataFrame
                    if metric_file.endswith(".csv"):
                        metric_data.to_csv(metric_file)
                    elif metric_file.endswith(".parquet"):
                        metric_data.to_parquet(metric_file)
                    elif metric_file.endswith(".h5") or metric_file.endswith(".hdf5"):
                        metric_data.to_hdf(metric_file, key="metrics")
                    elif metric_file.endswith(".json"):
                        metric_data.to_json(metric_file, orient="records")
                    elif metric_file.endswith(".feather"):
                        metric_data.to_feather(metric_file)
                    else:
                        # Default to CSV
                        metric_data.to_csv(metric_file)
                else:
                    # For other formats, save the already formatted data
                    with open(metric_file, "wb" if isinstance(metric_data, bytes) else "w") as f:
                        f.write(metric_data)
                
                files_saved += 1
                
                # Print individual metric summary for pandas data
                if isinstance(metric_data, pd.DataFrame):
                    console.print(f"   [bold]Metric summary:[/bold] {len(metric_data)} rows, {len(metric_data.columns)} columns")
            
            console.print(f"[bold green]Success![/bold green] {files_saved} metric files saved")

    except (ConnectionError, ValueError, IOError, requests.RequestException) as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        if verbose:
            console.print(traceback.format_exc())


if __name__ == "__main__":
    cli()
