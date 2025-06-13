# Metrics Extractor

A Python tool to extract metrics from Prometheus and InfluxDB and store them locally in various formats for analysis and visualization.

## Features

- Extract metrics from Prometheus and InfluxDB
- Specify time intervals or extract all historical data
- Choose which metrics to extract or extract all available metrics
- Save data in various formats (Parquet, HDF5, CSV, JSON, Feather)
- Extract each metric to separate files for better organization (or optionally combine them)
- Use as a command-line tool or as a Python library
- Return data in formats compatible with common Python data libraries (pandas, numpy)
- Extract all datapoints at maximum available resolution

## Quick Start

### Command Line Usage

By default, each metric will be saved to a separate file for better organization:

```bash
# Extract multiple metrics from Prometheus to separate files
metrics-extractor extract \
    --source prometheus \
    --url http://prometheus:9090 \
    --metrics "http_requests_total,node_cpu_seconds_total" \
    --from "2023-01-01T00:00:00Z" \
    --to "2023-01-02T00:00:00Z" \
    --format parquet \
    --output-file ./metrics.parquet
```

This will create files like `metrics_http_requests_total.parquet` and `metrics_node_cpu_seconds_total.parquet`.

You can also use the legacy behavior to combine metrics into a single file:

```bash
# Extract metrics to a single combined file
metrics-extractor extract \
    --source prometheus \
    --url http://prometheus:9090 \
    --metrics "http_requests_total,node_cpu_seconds_total" \
    --from "2023-01-01T00:00:00Z" \
    --to "2023-01-02T00:00:00Z" \
    --format parquet \
    --output-file ./metrics.parquet \
    --combined-output
```

### Python API Usage

When extracting multiple metrics, the library returns a dictionary with metric names as keys:

```python
from metrics_extractor import MetricsExtractor, PrometheusSource
from datetime import datetime

# Initialize
prometheus = PrometheusSource(url="http://prometheus:9090")
extractor = MetricsExtractor()

# Extract multiple metrics (returns a dictionary of metric data)
metrics_data = extractor.extract(
    source=prometheus,
    metrics=["http_requests_total", "node_cpu_seconds_total"],
    from_time=datetime(2023, 1, 1),
    to_time=datetime(2023, 1, 2),
    output_format="pandas"
)

# Access individual metrics
http_requests = metrics_data["http_requests_total"]
cpu_seconds = metrics_data["node_cpu_seconds_total"]

print(http_requests.head())

# Save individual metrics if needed
http_requests.to_parquet("http_requests.parquet")
cpu_seconds.to_parquet("cpu_seconds.parquet")

# You can also use the legacy behavior to get a combined dataset
combined_data = extractor.extract(
    source=prometheus,
    metrics=["http_requests_total", "node_cpu_seconds_total"],
    from_time=datetime(2023, 1, 1),
    to_time=datetime(2023, 1, 2),
    output_format="pandas",
    separate_metrics=False  # Use this to get the combined data
)
```

## Requirements

- Python 3.8+
- pandas
- numpy
- prometheus-api-client
- influxdb-client
- pyarrow
- tables (for HDF5)
- click (for CLI)
