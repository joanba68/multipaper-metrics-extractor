"""
Core module for extracting metrics data.
"""

import concurrent.futures
from datetime import datetime, timedelta
from typing import Any, Dict, Iterator, List, Optional, Union

import pandas as pd

from metrics_extractor.core.datasource import DataSource
from metrics_extractor.core.formatter import get_formatter


class MetricsExtractor:
    """
    Main interface for extracting metrics from various data sources.
    """

    def extract(
        self,
        source: DataSource,
        metrics: Optional[List[str]] = None,
        from_time: Optional[datetime] = None,
        to_time: Optional[datetime] = None,
        output_format: str = "pandas",
        separate_metrics: bool = True,
    ) -> Union[Any, Dict[str, Any]]:
        """
        Extract metrics from the specified source.

        Args:
            source: The data source to extract metrics from
            metrics: List of metrics to extract. If None, extract all available metrics.
            from_time: Start time for the extraction. If None, use the earliest available time.
            to_time: End time for the extraction. If None, use the latest available time.
            output_format: Format to return the data in ("pandas", "numpy", "dict", etc.)
            separate_metrics: If True, return a dictionary with a separate entry for each metric.
                             If False, return a combined dataset (legacy behavior).

        Returns:
            Union[Any, Dict[str, Any]]: Either a single formatted dataset (if separate_metrics=False)
            or a dictionary mapping metric names to their respective formatted datasets.

        Raises:
            ConnectionError: If connection to the data source fails
            ValueError: If the specified metrics, time range, or output format is invalid
        """
        # Ensure connection to the data source
        source.connect()

        # If separate_metrics is False, use the original behavior
        if not separate_metrics:
            data = source.get_data(metrics, from_time, to_time)
            formatter = get_formatter(output_format)
            return formatter(data)

        # Get available metrics if not specified
        if metrics is None:
            metrics = source.get_metrics()

        # Process each metric separately
        results = {}
        for metric in metrics:
            data = source.get_data([metric], from_time, to_time)
            formatter = get_formatter(output_format)
            results[metric] = formatter(data)

        return results

    def extract_parallel(
        self,
        source: DataSource,
        metrics: List[str],
        from_time: Optional[datetime] = None,
        to_time: Optional[datetime] = None,
        output_format: str = "pandas",
        max_workers: int = 4,
        separate_metrics: bool = True,
    ) -> Union[Any, Dict[str, Any]]:
        """
        Extract multiple metrics in parallel.

        This method extracts each metric separately in parallel and can return either
        a combined result or a dictionary with separate results for each metric.

        Args:
            source: The data source to extract metrics from
            metrics: List of metrics to extract (must be provided for parallel extraction)
            from_time: Start time for the extraction
            to_time: End time for the extraction
            output_format: Format to return the data in
            max_workers: Maximum number of parallel workers
            separate_metrics: If True, return a dictionary with a separate entry for each metric.
                             If False, return a combined dataset (legacy behavior).

        Returns:
            Union[Any, Dict[str, Any]]: Either a single formatted dataset (if separate_metrics=False)
            or a dictionary mapping metric names to their respective formatted datasets.

        Raises:
            ConnectionError: If connection to the data source fails
            ValueError: If the specified metrics, time range, or output format is invalid
        """
        if not metrics:
            raise ValueError("Metrics list must be provided for parallel extraction")

        # Ensure connection to the data source
        source.connect()

        # Extract each metric in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(
                    self.extract,
                    source=source,
                    metrics=[metric],
                    from_time=from_time,
                    to_time=to_time,
                    output_format="pandas",  # Always use pandas for intermediate results
                    separate_metrics=False,  # Get individual metric results without nesting
                ): metric
                for metric in metrics
            }

            # Collect results
            results = {}
            for future in concurrent.futures.as_completed(futures):
                metric = futures[future]
                results[metric] = future.result()

        # If separate_metrics is False, combine the results
        if not separate_metrics:
            if results:
                # Convert all results to pandas dataframes for concatenation
                pandas_results = []
                for result in results.values():
                    # Convert back to pandas if needed
                    if not isinstance(result, pd.DataFrame):
                        # This is a fallback and might not work for all formats
                        # Better to use pandas directly for intermediate results
                        result = pd.DataFrame(result)
                    pandas_results.append(result)
                
                combined_data = pd.concat(pandas_results) if pandas_results else pd.DataFrame()
                formatter = get_formatter(output_format)
                return formatter(combined_data)
            return get_formatter(output_format)(pd.DataFrame())
        
        # Format each result according to the requested output format
        formatted_results = {}
        for metric, result in results.items():
            formatter = get_formatter(output_format)
            # If the result is already a pandas DataFrame, format it
            if isinstance(result, pd.DataFrame):
                formatted_results[metric] = formatter(result)
            else:
                # If it's already in the requested format, keep it as is
                formatted_results[metric] = result
                
        return formatted_results

    def extract_incremental(
        self,
        source: DataSource,
        metrics: Optional[List[str]] = None,
        from_time: Optional[datetime] = None,
        to_time: Optional[datetime] = None,
        chunk_size: timedelta = timedelta(days=1),
        output_format: str = "pandas",
        separate_metrics: bool = True,
    ) -> Iterator[Union[Any, Dict[str, Any]]]:
        """
        Extract data incrementally in chunks.

        This method is a generator that yields chunks of data for the specified
        time range, divided into intervals of the specified chunk size.

        Args:
            source: The data source to extract metrics from
            metrics: List of metrics to extract
            from_time: Start time for the extraction
            to_time: End time for the extraction
            chunk_size: Size of each time chunk
            output_format: Format to return the data in
            separate_metrics: If True, yield dictionaries with separate entries for each metric.
                             If False, yield combined datasets (legacy behavior).

        Yields:
            Union[Any, Dict[str, Any]]: Chunks of data in the specified format

        Raises:
            ConnectionError: If connection to the data source fails
            ValueError: If the specified metrics, time range, or output format is invalid
        """
        # Ensure connection to the data source
        source.connect()

        # Get available metrics if not specified
        if metrics is None:
            metrics = source.get_metrics()

        # Get actual time range if not specified
        if from_time is None or to_time is None:
            # Get a small sample to determine time range
            sample_data = source.get_data(metrics, None, None)
            if sample_data.empty:
                # No data available
                return

            # Use actual time range from data if not specified
            if from_time is None:
                from_time = sample_data.index.min()
            if to_time is None:
                to_time = sample_data.index.max()
        
        # Ensure we have valid datetime objects for from_time and to_time
        if from_time is None or to_time is None:
            raise ValueError("Could not determine time range for incremental extraction")

        # Extract data in chunks
        current_time = from_time
        while current_time < to_time:
            chunk_end = min(current_time + chunk_size, to_time)

            if separate_metrics:
                # Process each metric separately
                chunk_results = {}
                for metric in metrics:
                    chunk_data = source.get_data([metric], current_time, chunk_end)
                    formatter = get_formatter(output_format)
                    chunk_results[metric] = formatter(chunk_data)
                yield chunk_results
            else:
                # Original behavior - combined results
                chunk_data = source.get_data(metrics, current_time, chunk_end)
                formatter = get_formatter(output_format)
                yield formatter(chunk_data)

            # Move to the next chunk
            current_time = chunk_end
