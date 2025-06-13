"""
InfluxDB data source adapter.
"""

from datetime import datetime, timezone, timedelta
from typing import List, Optional

import pandas as pd
from influxdb_client.client.influxdb_client import InfluxDBClient
from influxdb_client.client.flux_table import FluxTable

from metrics_extractor.core.datasource import DataSource
from metrics_extractor.core.logging import logger


class InfluxDBSource(DataSource):
    """
    Data source adapter for InfluxDB.
    """

    def __init__(
        self,
        url: str,
        token: str,
        org: str,
        bucket: str,
        measurement: Optional[str] = None,
    ):
        """
        Initialize an InfluxDB data source.

        Args:
            url: URL of the InfluxDB server
            token: API token for authentication
            org: Organization name
            bucket: Bucket name
            measurement: Optional measurement name to filter by
        """
        self.url = url
        self.token = token
        self.org = org
        self.bucket = bucket
        self.measurement = measurement
        self.client = None

    def connect(self) -> None:
        """
        Establish connection to the InfluxDB server.

        Raises:
            ConnectionError: If connection to InfluxDB fails
        """
        try:
            self.client = InfluxDBClient(
                url=self.url,
                token=self.token,
                org=self.org,
            )
            # Test connection by querying health
            health = self.client.health()
            if health.status != "pass":
                raise ConnectionError(f"InfluxDB health check failed: {health.message}")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to InfluxDB: {e}") from e

    def get_metrics(self) -> List[str]:
        """
        Get list of available metrics from InfluxDB.

        Returns:
            List[str]: List of metric names (field keys)

        Raises:
            ConnectionError: If connection to InfluxDB fails
        """
        if not self.client:
            self.connect()

        try:
            # Construct a Flux query to get all field keys
            query = f"""
                import "influxdata/influxdb/schema"

                schema.fieldKeys(
                    bucket: "{self.bucket}",
                    predicate: (r) => true
                )
            """

            # Execute the query
            result = self.client.query_api().query(query, org=self.org)

            # Extract the field keys
            metrics = []
            for table in result:
                for record in table.records:
                    metrics.append(record.values.get("_value"))

            return metrics
        except Exception as e:
            raise ConnectionError(f"Failed to get metrics from InfluxDB: {e}") from e

    def get_data(
        self,
        metrics: Optional[List[str]],
        from_time: Optional[datetime],
        to_time: Optional[datetime],
    ) -> pd.DataFrame:
        """
        Get data for specified metrics and time range from InfluxDB.

        Args:
            metrics: List of metrics to extract. If None, extract all available metrics.
            from_time: Start time for the extraction. If None, use the earliest available time.
            to_time: End time for the extraction. If None, use the latest available time.

        Returns:
            pd.DataFrame: A DataFrame containing the extracted metrics data

        Raises:
            ConnectionError: If connection to InfluxDB fails
            ValueError: If the specified metrics or time range is invalid
        """
        if not self.client:
            self.connect()

        # If no metrics specified, get all metrics
        if metrics is None:
            metrics = self.get_metrics()

        # Default time range if not specified
        if to_time is None:
            to_time = datetime.now(timezone.utc)
        if from_time is None:
            # Default to 1 hour ago if not specified
            from_time = to_time - timedelta(hours=1)

        # Ensure times are in UTC
        from_time_utc = self._ensure_utc(from_time)
        to_time_utc = self._ensure_utc(to_time)

        logger.info("Using UTC time range: %s to %s", from_time_utc, to_time_utc)

        # Construct time range filters
        time_range_filter = ""
        if from_time_utc is not None:
            from_time_str = from_time_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
            time_range_filter += f" |> range(start: {from_time_str}"

            if to_time_utc is not None:
                to_time_str = to_time_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
                time_range_filter += f", stop: {to_time_str}"

            time_range_filter += ")"
        elif to_time_utc is not None:
            to_time_str = to_time_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
            time_range_filter += f" |> range(stop: {to_time_str})"

        # Construct measurement filter
        measurement_filter = ""
        if self.measurement:
            measurement_filter = f' |> filter(fn: (r) => r._measurement == "{self.measurement}")'

        # Construct field filter for metrics
        metrics_str = ", ".join([f'"{m}"' for m in metrics])
        field_filter = f" |> filter(fn: (r) => contains(value: r._field, set: [{metrics_str}]))"

        # Construct the complete query
        query = f"""
            from(bucket: "{self.bucket}")
            {time_range_filter}
            {measurement_filter}
            {field_filter}
        """

        logger.info("Executing Flux query: %s", query)

        try:
            # Ensure client is connected
            if not self.client:
                self.connect()
                
            # Execute the query
            result = self.client.query_api().query(query, org=self.org)

            # Convert the result to a DataFrame
            df = self._flux_to_dataframe(result)
            
            # If empty, try with a more generous time range
            if df.empty:
                logger.warning("No data found, trying with extended time range")
                # Try with extended time range (1 day before and after)
                extended_from = from_time_utc - timedelta(days=1)
                extended_to = to_time_utc + timedelta(days=1)
                
                # Create a new query with extended time range
                ext_from_str = extended_from.strftime("%Y-%m-%dT%H:%M:%SZ")
                ext_to_str = extended_to.strftime("%Y-%m-%dT%H:%M:%SZ")
                
                extended_query = f"""
                    from(bucket: "{self.bucket}")
                    |> range(start: {ext_from_str}, stop: {ext_to_str})
                    {measurement_filter}
                    {field_filter}
                """
                
                logger.info("Trying extended time range: %s to %s", extended_from, extended_to)
                logger.info("Extended query: %s", extended_query)
                
                # Ensure client is connected
                if not self.client:
                    self.connect()
                    
                result = self.client.query_api().query(extended_query, org=self.org)
                df = self._flux_to_dataframe(result)
                
                # Filter the results to match the original time range as closely as possible
                if not df.empty:
                    from_timestamp = from_time_utc.timestamp()
                    to_timestamp = to_time_utc.timestamp()
                    
                    # Convert index to Unix timestamps for comparison
                    unix_timestamps = df.index.map(lambda x: x.timestamp())
                    
                    # Use a more relaxed filter - get data within original time frame if possible
                    # otherwise keep all data from extended query
                    in_range = (unix_timestamps >= from_timestamp) & (unix_timestamps <= to_timestamp)
                    if in_range.any():
                        df = df[in_range]
            
            return df
        except Exception as e:
            raise ConnectionError(f"Failed to get data from InfluxDB: {e}") from e

    def _flux_to_dataframe(self, tables: List[FluxTable]) -> pd.DataFrame:
        """
        Convert Flux query result to a pandas DataFrame.

        Args:
            tables: List of FluxTable objects from the query result

        Returns:
            pd.DataFrame: A DataFrame containing the query result
        """
        # Extract records from all tables
        records = []
        for table in tables:
            for record in table.records:
                # Extract the values
                record_dict = {
                    "timestamp": record.get_time(),
                    "value": record.get_value(),
                    "metric": record.values.get("_field"),
                }

                # Add tags as columns
                for key, value in record.values.items():
                    if key.startswith("_"):
                        # Skip internal fields
                        continue
                    record_dict[key] = value

                records.append(record_dict)

        # Create DataFrame
        if records:
            df = pd.DataFrame(records)
            logger.info("Created DataFrame with %d records", len(records))

            # Set timestamp as index
            df.set_index("timestamp", inplace=True)

            return df
        # Return empty DataFrame with proper columns
        logger.warning("No records found in query result")
        return pd.DataFrame(columns=["metric", "value"])

    def _ensure_utc(self, dt: datetime) -> datetime:
        """
        Ensure a datetime object is in UTC timezone.
        
        Args:
            dt: The datetime object to convert
            
        Returns:
            datetime: The datetime object in UTC timezone
        """
        if dt is None:
            return None
            
        # If the datetime has no timezone info, assume it's in local time and convert to UTC
        if dt.tzinfo is None:
            # Convert naive datetime to UTC by assuming it's in local time
            local_dt = dt.replace(tzinfo=datetime.now().astimezone().tzinfo)
            return local_dt.astimezone(timezone.utc)
        elif dt.tzinfo != timezone.utc:
            # If it has timezone info but not UTC, convert to UTC
            return dt.astimezone(timezone.utc)
            
        # Already in UTC
        return dt
