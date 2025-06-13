"""
Metrics Extractor - A tool for extracting metrics from various data sources.
"""

__version__ = "0.1.0"

from metrics_extractor.core.extractor import MetricsExtractor
from metrics_extractor.core.logging import logger, setup_logging
from metrics_extractor.datasources.influxdb import InfluxDBSource
from metrics_extractor.datasources.prometheus import PrometheusSource
from metrics_extractor.formatters import register_formatter

__all__ = [
    "MetricsExtractor",
    "PrometheusSource",
    "InfluxDBSource",
    "register_formatter",
    "logger",
    "setup_logging",
]
