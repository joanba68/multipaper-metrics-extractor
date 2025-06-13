"""
Abstract base class for data sources.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

import pandas as pd


class DataSource(ABC):
    """
    Abstract base class for data sources.

    All data sources must implement these methods to be compatible with the
    MetricsExtractor.
    """

    @abstractmethod
    def connect(self) -> None:
        """
        Establish connection to the data source.

        This method should handle authentication, connection setup, and
        validation.

        Raises:
            ConnectionError: If connection to the data source fails.
        """

    @abstractmethod
    def get_metrics(self) -> List[str]:
        """
        Get list of available metrics.

        Returns:
            List[str]: List of metric names available in the data source.

        Raises:
            ConnectionError: If connection to the data source fails.
        """

    @abstractmethod
    def get_data(
        self,
        metrics: Optional[List[str]],
        from_time: Optional[datetime],
        to_time: Optional[datetime],
    ) -> pd.DataFrame:
        """
        Get data for specified metrics and time range.

        Args:
            metrics: List of metrics to extract. If None, extract all available metrics.
            from_time: Start time for the extraction. If None, use the earliest available time.
            to_time: End time for the extraction. If None, use the latest available time.

        Returns:
            pd.DataFrame: A DataFrame containing the extracted metrics data.

        Raises:
            ConnectionError: If connection to the data source fails.
            ValueError: If the specified metrics or time range is invalid.
        """
