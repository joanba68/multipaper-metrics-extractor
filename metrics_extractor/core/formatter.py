"""
Output formatter module for metrics data.
"""

import io
from typing import Any, Callable, Dict

import pandas as pd

# Registry for output formatters
_formatters: Dict[str, Callable[[pd.DataFrame], Any]] = {}


def register_formatter(name: str, formatter_func: Callable[[pd.DataFrame], Any]) -> None:
    """
    Register a custom output formatter.

    Args:
        name: Name of the formatter
        formatter_func: Function that takes a DataFrame and returns formatted data
    """
    _formatters[name] = formatter_func


def get_formatter(format_name: str) -> Callable[[pd.DataFrame], Any]:
    """
    Get a formatter by name.

    Args:
        format_name: Name of the formatter

    Returns:
        Callable: Formatter function

    Raises:
        ValueError: If the formatter is not registered
    """
    if format_name not in _formatters:
        raise ValueError(f"Unknown formatter: {format_name}")
    return _formatters[format_name]


def _format_pandas(data: pd.DataFrame) -> pd.DataFrame:
    """Return the data as a pandas DataFrame."""
    return data


def _format_numpy(data: pd.DataFrame) -> Dict[str, Any]:
    """Convert the data to a dictionary of numpy arrays."""
    return {col: data[col].values for col in data.columns}


def _format_dict(data: pd.DataFrame) -> Dict[str, Any]:
    """Convert the data to a dictionary of Python lists."""
    return data.to_dict(orient="list")


def _format_csv(data: pd.DataFrame) -> str:
    """Convert the data to a CSV string."""
    return data.to_csv()


def _format_json(data: pd.DataFrame) -> str:
    """Convert the data to a JSON string."""
    return data.to_json(orient="records")


def _format_parquet(data: pd.DataFrame) -> bytes:
    """Convert the data to Parquet format."""

    buffer = io.BytesIO()
    data.to_parquet(buffer)
    return buffer.getvalue()


def _format_hdf5(data: pd.DataFrame) -> bytes:
    """Convert the data to HDF5 format."""

    buffer = io.BytesIO()
    data.to_hdf(buffer, key="metrics", mode="w")
    return buffer.getvalue()


def _format_feather(data: pd.DataFrame) -> bytes:
    """Convert the data to Feather format."""

    buffer = io.BytesIO()
    data.to_feather(buffer)
    return buffer.getvalue()


# Register the built-in formatters
register_formatter("pandas", _format_pandas)
register_formatter("numpy", _format_numpy)
register_formatter("dict", _format_dict)
register_formatter("csv", _format_csv)
register_formatter("json", _format_json)
register_formatter("parquet", _format_parquet)
register_formatter("hdf5", _format_hdf5)
register_formatter("feather", _format_feather)
