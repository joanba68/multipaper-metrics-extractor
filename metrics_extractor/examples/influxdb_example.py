#!/usr/bin/env python3
"""
Simple example of using the Metrics Extractor API with InfluxDB.
"""

from datetime import datetime, timedelta, timezone

import matplotlib.pyplot as plt
import pandas as pd

from metrics_extractor import MetricsExtractor, InfluxDBSource, logger, setup_logging


def main():
    """
    Extract metrics from InfluxDB and plot them.
    """
    # Configure the logger to show INFO level messages
    setup_logging(level="INFO")

    # Replace with your InfluxDB configuration
    influxdb_url = "http://localhost:37963/"
    influxdb_token = "multipaper"
    influxdb_org = "multipaper"
    influxdb_bucket = "multipaper"

    try:
        # Initialize the InfluxDB data source
        logger.info("Creating InfluxDB data source...")
        influxdb = InfluxDBSource(
            url=influxdb_url,
            token=influxdb_token,
            org=influxdb_org,
            bucket=influxdb_bucket
        )

        # Print available metrics
        logger.info("Connecting to InfluxDB...")
        metrics = influxdb.get_metrics()
        logger.info("Available metrics: %d", len(metrics))
        if metrics:
            logger.info("Sample metrics: %s", metrics[:5])

        # Create a metrics extractor
        extractor = MetricsExtractor()

        # Define the time range for extraction - explicitly using UTC
        # Since Prometheus data stored in InfluxDB is in UTC
        to_time = datetime.now(timezone.utc)
        from_time = to_time - timedelta(hours=5)  # Using larger time window (24h)
        
        logger.info("Using explicit UTC time range for extraction")
        logger.info("From: %s", from_time)
        logger.info("To: %s", to_time)

        # Choose some metrics to extract - try with metrics from sample output
        # Using metrics from the log output that were shown in the InfluxDB
        selected_metrics = ["mc_tps", "minecraft_players_count"]
        # if metrics:
        #     # Use the first couple of metrics from what's available if different
        #     if len(metrics) >= 2:
        #         selected_metrics = metrics[:2]
        #     else:
        #         selected_metrics = metrics
            
        if not selected_metrics:
            logger.warning("No metrics available to extract")
            return

        logger.info("Extracting metrics: %s", selected_metrics)

        # Extract the metrics - each metric will be returned as a separate entry in the dictionary
        metrics_data = extractor.extract(
            source=influxdb,
            metrics=selected_metrics,
            from_time=from_time,
            to_time=to_time,
            output_format="pandas",
        )

        # Print the extracted data
        logger.info("\nExtracted data:")
        logger.info("Number of metrics: %d", len(metrics_data))
        
        # Process each metric separately
        for metric_name, data in metrics_data.items():
            logger.info("\nMetric: %s", metric_name)
            logger.info("Shape: %s", data.shape)
            
            if not data.empty:
                logger.info("Time range in data: %s to %s", data.index.min(), data.index.max())
                logger.info("Sample data:")
                logger.debug("\n%s", data.head())
                
                # Save the data to different formats
                logger.info("Saving %s to different formats...", metric_name)

                # CSV
                data.to_csv(f"influxdb_metrics_{metric_name}.csv")
                logger.info("Saved to influxdb_metrics_%s.csv", metric_name)

                # Parquet
                data.to_parquet(f"influxdb_metrics_{metric_name}.parquet")
                logger.info("Saved to influxdb_metrics_%s.parquet", metric_name)

                # JSON
                data.to_json(f"influxdb_metrics_{metric_name}.json", orient="records")
                logger.info("Saved to influxdb_metrics_%s.json", metric_name)
            else:
                logger.warning("No data found for metric %s in the specified time range", metric_name)

        # Check if we have any data to plot
        has_data = any(not data.empty for data in metrics_data.values())
        
        # Only proceed with plotting if we have data
        if has_data:
            # Plot the data
            try:
                logger.info("Creating plot...")
                plt.figure(figsize=(12, 6))

                # Plot each metric
                for metric_name, data in metrics_data.items():
                    if not data.empty:
                        plt.plot(data.index, data["value"], label=metric_name)

                plt.title("Metrics from InfluxDB")
                plt.xlabel("Time")
                plt.ylabel("Value")
                plt.legend()
                plt.grid(True)

                # Save the plot
                plt.savefig("influxdb_metrics_plot.png")
                logger.info("Plot saved to influxdb_metrics_plot.png")

                # Show the plot if running interactively
                plt.show()

            except Exception as e:
                logger.error("Error creating plot: %s", e)
        else:
            logger.warning("Skipping plotting as no data was retrieved")

    except ConnectionError as e:
        logger.error("Connection error: %s", e)
    except Exception as e:
        logger.error("Error: %s", e, exc_info=True)


if __name__ == "__main__":
    main()
