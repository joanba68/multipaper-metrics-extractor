"""
Prometheus data source adapter.
"""

from datetime import datetime, timedelta
import re
from typing import Dict, List, Optional

import pandas as pd
import requests
from prometheus_api_client import PrometheusConnect

from metrics_extractor.core.datasource import DataSource
from metrics_extractor.core.logging import logger


class PrometheusSource(DataSource):
    """
    Data source adapter for Prometheus.
    """

    def __init__(
        self,
        url: str,
        auth: Optional[Dict[str, str]] = None,
        verify: bool = True,
        headers: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize a Prometheus data source.

        Args:
            url: URL of the Prometheus server
            auth: Authentication details (e.g., {"username": "user", "password": "pass"})
            verify: Whether to verify SSL certificates
            headers: Additional HTTP headers
        """
        self.url = url
        self.auth = auth
        self.verify = verify
        self.headers = headers if headers is not None else {}
        self.client = None

    def connect(self) -> None:
        """
        Establish connection to the Prometheus server.

        Raises:
            ConnectionError: If connection to Prometheus fails
        """
        try:
            self.client = PrometheusConnect(
                url=self.url,
                headers=self.headers,
                disable_ssl=not self.verify,
            )
            # Test connection by fetching a simple metric
            self.client.get_current_metric_value("up")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Prometheus: {e}") from e

    def get_metrics(self) -> List[str]:
        """
        Get list of available metrics from Prometheus.

        Returns:
            List[str]: List of metric names

        Raises:
            ConnectionError: If connection to Prometheus fails
        """
        if not self.client:
            self.connect()

        try:
            return self.client.all_metrics()
        except Exception as e:
            raise ConnectionError(f"Failed to get metrics from Prometheus: {e}") from e

    def _is_function_query(self, query: str) -> bool:
        """
        Check if the query contains Prometheus functions.

        Args:
            query: The query string to check

        Returns:
            bool: True if the query contains functions, False otherwise
        """
        # Pattern to match functions like rate(), sum(), etc.
        function_pattern = r'[a-zA-Z_:][a-zA-Z0-9_:]*\('
        return bool(re.findall(function_pattern, query.strip()))

    def get_data(
        self,
        metrics: Optional[List[str]],
        from_time: Optional[datetime],
        to_time: Optional[datetime],
    ) -> pd.DataFrame:
        """
        Get data for specified metrics and time range from Prometheus.

        For simple metrics, uses range vector selectors to get all raw datapoints within the time range.
        For function queries (e.g., rate(http_requests_total[5m])), uses query_range with 1s step.

        Args:
            metrics: List of metrics to extract. If None, extract all available metrics.
            from_time: Start time for the extraction. If None, use the earliest available time.
            to_time: End time for the extraction. If None, use the latest available time.

        Returns:
            pd.DataFrame: A DataFrame containing the extracted metrics data

        Raises:
            ConnectionError: If connection to Prometheus fails
            ValueError: If the specified metrics or time range is invalid
        """
        # Ensure client is initialized
        if not self.client:
            self.connect()

        # If no metrics specified, get all metrics
        if metrics is None:
            metrics = self.get_metrics()

        # Default time range if not specified
        if to_time is None:
            to_time = datetime.now()
        if from_time is None:
            # Default to 1 hour ago if not specified
            from_time = to_time - timedelta(hours=1)

        all_data = []

        for metric in metrics:
            try:
                # Calculate the time range duration in seconds
                time_range_seconds = int((to_time - from_time).total_seconds())
                
                if self._is_function_query(metric):
                    # Handle function queries with query_range and 1s step
                    logger.info("Handling function query: %s", metric)
                    
                    # Use query_range for function queries with a 1s step
                    # Ensure client is not None before calling custom_query_range
                    if not self.client:
                        self.connect()
                    
                    result = self.client.custom_query_range(
                        query=metric,
                        start_time=from_time,
                        end_time=to_time,
                        step="1s"  # 1 second resolution
                    )
                    
                    # Process the results from query_range
                    for item in result:
                        # Extract the metric name and labels
                        metric_name = metric  # Use the original query as the metric name
                        labels = {k: v for k, v in item["metric"].items() if k != "__name__"}
                        
                        # Extract the values
                        values = item.get("values", [])
                        
                        if values:
                            # Create a DataFrame with timestamps and values
                            df = pd.DataFrame(values, columns=["timestamp", "value"])
                            
                            # Convert timestamp to datetime
                            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
                            
                            # Convert value to float
                            df["value"] = df["value"].astype(float)
                            
                            # Set timestamp as index
                            df.set_index("timestamp", inplace=True)
                            
                            # Add metric name and labels as columns
                            df["metric"] = metric_name
                            for label, value in labels.items():
                                df[label] = value
                            
                            all_data.append(df)
                else:
                    # Use the original approach for simple metrics with range vector
                    # Create the range vector query with the exact time range
                    range_query = f"{metric}[{time_range_seconds}s]"
                    logger.info("Using range vector query: %s @ %s", range_query, to_time)

                    # Ensure client is not None before calling custom_query
                    if not self.client:
                        self.connect()
                        
                    # Execute the query at the end time to get all data points in the range
                    result = self.client.custom_query(
                        query=range_query,
                        params={"time": to_time.timestamp()},
                    )

                    # Process the results
                    for item in result:
                        # Extract the metric name and labels
                        metric_name = item["metric"]["__name__"]
                        labels = {k: v for k, v in item["metric"].items() if k != "__name__"}

                        # Extract the values (for range vectors, they're in the 'values' field)
                        values = item.get("values", [])

                        if values:
                            # Create a DataFrame with timestamps and values
                            df = pd.DataFrame(values, columns=["timestamp", "value"])

                            # Convert timestamp to datetime without timezone
                            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")

                            # Try to compare by converting timestamps to Unix timestamps (seconds since epoch)
                            # This avoids timezone issues completely
                            from_timestamp = from_time.timestamp()
                            to_timestamp = to_time.timestamp()

                            # Convert dataframe timestamps to Unix timestamps for comparison
                            unix_timestamps = df["timestamp"].map(lambda x: x.timestamp())

                            # Check how many are in range
                            in_range = (unix_timestamps >= from_timestamp) & (
                                unix_timestamps <= to_timestamp
                            )

                            # Apply the filter
                            df = df[in_range]

                            # If still empty after precise filtering, try with a more generous time
                            # range
                            if df.empty:
                                logger.warning("No data after filtering. Using extended time range.")
                                # Try with extended time range (1 hour before and after)
                                extended_from = from_time - timedelta(hours=1)
                                extended_to = to_time + timedelta(hours=1)
                                logger.info("Extended range: %s to %s", extended_from, extended_to)

                                # Convert to timestamps
                                ext_from_ts = extended_from.timestamp()
                                ext_to_ts = extended_to.timestamp()

                                # Create new dataframe from original values
                                df = pd.DataFrame(values, columns=["timestamp", "value"])
                                df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
                                unix_timestamps = df["timestamp"].map(lambda x: x.timestamp())

                                # Filter with extended range
                                df = df[
                                    (unix_timestamps >= ext_from_ts) & (unix_timestamps <= ext_to_ts)
                                ]

                                # If still empty, use all data as last resort
                                if df.empty:
                                    logger.warning(
                                        "No data even with extended range. Using all available data."
                                    )
                                    df = pd.DataFrame(values, columns=["timestamp", "value"])
                                    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")

                            # Convert value to float
                            df["value"] = df["value"].astype(float)

                            # Set timestamp as index
                            df.set_index("timestamp", inplace=True)

                            # Add metric name and labels as columns
                            df["metric"] = metric_name
                            for label, value in labels.items():
                                df[label] = value

                            all_data.append(df)

            except (ConnectionError, ValueError, IOError, requests.RequestException) as e:
                # Log the error but continue with other metrics
                logger.warning("Failed to get data for metric %s: %s", metric, e)

        # Combine all DataFrames
        if all_data:
            return pd.concat(all_data)
        # Return empty DataFrame with proper columns
        return pd.DataFrame(columns=["metric", "value"])
