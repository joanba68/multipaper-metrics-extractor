#!/usr/bin/env python3
"""
Simple example of using the Metrics Extractor API.
"""

from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import pandas as pd
import logging

from metrics_extractor import MetricsExtractor, PrometheusSource


def main():
    """
    Extract metrics from Prometheus and plot them.
    """

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Replace with your Prometheus URL
    prometheus_url = "http://localhost:36837/"

    try:
        # Initialize the Prometheus data source
        logger.info("Creating Prometheus data source...")
        prometheus = PrometheusSource(url=prometheus_url)

        # Print available metrics
        logger.info("Connecting to Prometheus...")
        metrics = prometheus.get_metrics()
        logger.info("Available metrics: %d", len(metrics))
        if metrics:
            logger.info("Sample metrics: %s", metrics[:5])

        # Create a metrics extractor
        extractor = MetricsExtractor()

        # Define the time range for extraction
        to_time = datetime.now()
        from_time = to_time - timedelta(hours=5)

        # Choose some metrics to extract
        selected_metrics = ["mc_tps", "minecraft_players_count"]
        # if not all(metric in metrics for metric in selected_metrics):
        #     # If the specific metrics are not available, use the first available metric
        #     selected_metrics = [metrics[0]] if metrics else []

        if not selected_metrics:
            logger.warning("No metrics available to extract")
            return

        logger.info("Extracting metrics: %s", selected_metrics)
        logger.info("Time range: %s to %s", from_time, to_time)

        # Extract the metrics - returns a dictionary where each key is a metric name
        metrics_data = extractor.extract(
            source=prometheus,
            metrics=selected_metrics,
            from_time=from_time,
            to_time=to_time,
            output_format="pandas",
        )

        # Print the extracted data
        logger.info("\nExtracted data:")
        logger.info("Number of metrics: %s", len(metrics_data))
        
        # Process each metric
        for metric_name, data in metrics_data.items():
            logger.info("\nMetric: %s", metric_name)
            logger.info("Shape: %s", data.shape)
            logger.info("Sample data:")
            logger.debug("\n%s", data.head())

            # Save each metric to its own file
            logger.info("Saving %s to different formats...", metric_name)

            # CSV
            data.to_csv(f"metrics_{metric_name}.csv")
            logger.info("Saved to metrics_%s.csv", metric_name)

            # Parquet
            data.to_parquet(f"metrics_{metric_name}.parquet")
            logger.info("Saved to metrics_%s.parquet", metric_name)

            # JSON
            data.to_json(f"metrics_{metric_name}.json", orient="records")
            logger.info("Saved to metrics_%s.json", metric_name)

        # Create a combined DataFrame for plotting all metrics together
        combined_data = pd.DataFrame()
        for metric_name, data in metrics_data.items():
            if combined_data.empty:
                combined_data = data.copy()
            else:
                # Append data, preserving the metric name
                combined_data = pd.concat([combined_data, data])

        # Plot the data
        try:
            logger.info("Creating plot...")
            plt.figure(figsize=(12, 6))

            # Plot each metric
            for metric_name, data in metrics_data.items():
                plt.plot(data.index, data["value"], label=metric_name)

            plt.title("Metrics from Prometheus")
            plt.xlabel("Time")
            plt.ylabel("Value")
            plt.legend()
            plt.grid(True)

            # Save the plot
            plt.savefig("metrics_plot.png")
            logger.info("Plot saved to metrics_plot.png")

            # Show the plot if running interactively
            plt.show()

        except Exception as e:
            logger.error("Error creating plot: %s", e)

    except ConnectionError as e:
        logger.error("Connection error: %s", e)
    except Exception as e:
        logger.error("Error: %s", e, exc_info=True)


if __name__ == "__main__":
    main()
