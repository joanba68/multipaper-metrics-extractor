"""
Tests for the MetricsExtractor class.
"""

import unittest
from datetime import datetime, timedelta

import pandas as pd

from metrics_extractor.core.datasource import DataSource
from metrics_extractor.core.extractor import MetricsExtractor


class MockDataSource(DataSource):
    """Mock data source for testing."""

    def __init__(self):
        self.connect_called = False
        self.get_metrics_called = False
        self.get_data_called = False
        self.metrics = None
        self.from_time = None
        self.to_time = None

    def connect(self):
        self.connect_called = True

    def get_metrics(self):
        self.get_metrics_called = True
        return ["metric1", "metric2", "metric3"]

    def get_data(self, metrics, from_time, to_time):
        self.get_data_called = True
        self.metrics = metrics
        self.from_time = from_time
        self.to_time = to_time

        # Create a simple DataFrame with test data
        index = pd.date_range(
            start=from_time if from_time else datetime.now() - timedelta(hours=1),
            end=to_time if to_time else datetime.now(),
            freq="1min",
        )

        data = {
            "metric": [],
            "value": [],
        }

        for metric in metrics or ["metric1"]:
            for i in range(len(index)):
                data["metric"].append(metric)
                data["value"].append(i)

        df = pd.DataFrame(data, index=index * len(metrics or ["metric1"]))
        return df


class TestMetricsExtractor(unittest.TestCase):
    """Test cases for the MetricsExtractor class."""

    def test_extract_connects_to_source(self):
        """Test that extract connects to the data source."""
        source = MockDataSource()
        extractor = MetricsExtractor()

        extractor.extract(source=source)

        self.assertTrue(source.connect_called)

    def test_extract_gets_data_from_source(self):
        """Test that extract gets data from the data source."""
        source = MockDataSource()
        extractor = MetricsExtractor()

        extractor.extract(source=source)

        self.assertTrue(source.get_data_called)

    def test_extract_passes_metrics_to_source(self):
        """Test that extract passes the metrics to the data source."""
        source = MockDataSource()
        extractor = MetricsExtractor()

        metrics = ["metric1", "metric2"]
        extractor.extract(source=source, metrics=metrics)

        self.assertEqual(source.metrics, metrics)

    def test_extract_passes_time_range_to_source(self):
        """Test that extract passes the time range to the data source."""
        source = MockDataSource()
        extractor = MetricsExtractor()

        from_time = datetime(2023, 1, 1)
        to_time = datetime(2023, 1, 2)

        extractor.extract(
            source=source,
            from_time=from_time,
            to_time=to_time,
        )

        self.assertEqual(source.from_time, from_time)
        self.assertEqual(source.to_time, to_time)

    def test_extract_formats_data(self):
        """Test that extract formats the data according to the output format."""
        source = MockDataSource()
        extractor = MetricsExtractor()

        # Test with pandas format
        result_pandas = extractor.extract(
            source=source,
            output_format="pandas",
        )
        self.assertIsInstance(result_pandas, pd.DataFrame)

        # Test with dict format
        result_dict = extractor.extract(
            source=source,
            output_format="dict",
        )
        self.assertIsInstance(result_dict, dict)

        # Test with json format
        result_json = extractor.extract(
            source=source,
            output_format="json",
        )
        self.assertIsInstance(result_json, str)

    def test_handle_gaps(self):
        """Test that _handle_gaps correctly handles gaps in the data."""
        extractor = MetricsExtractor()

        # Create a DataFrame with gaps
        index = pd.date_range(
            start=datetime(2023, 1, 1),
            end=datetime(2023, 1, 2),
            freq="1h",
        )

        data = {
            "value": [1, None, 3, None, 5],
        }

        df = pd.DataFrame(data, index=index[:5])

        # Test interpolation
        result_interpolate = extractor._handle_gaps(df, "interpolate")
        self.assertFalse(result_interpolate["value"].isna().any())
        self.assertEqual(result_interpolate["value"][1], 2.0)

        # Test forward fill
        result_ffill = extractor._handle_gaps(df, "ffill")
        self.assertFalse(result_ffill["value"].isna().any())
        self.assertEqual(result_ffill["value"][1], 1.0)

        # Test backward fill
        result_bfill = extractor._handle_gaps(df, "bfill")
        self.assertFalse(result_bfill["value"].isna().any())
        self.assertEqual(result_bfill["value"][1], 3.0)


if __name__ == "__main__":
    unittest.main()
