#!/usr/bin/env python3
"""
CSV Analytics MCP Server
==========================
Spreadsheet and CSV analysis toolkit for AI agents. Load CSV files, query data
with SQL-like syntax, compute statistics, create aggregations, pivot tables,
and export chart-ready data.

By MEOK AI Labs | https://meok.ai

Install: pip install mcp pandas
Run:     python server.py
"""

import io
import json
import os
import tempfile
from datetime import datetime, timedelta
from typing import Any, Optional
from collections import defaultdict
from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------
FREE_DAILY_LIMIT = 30
_usage: dict[str, list[datetime]] = defaultdict(list)


def _check_rate_limit(caller: str = "anonymous") -> Optional[str]:
    now = datetime.now()
    cutoff = now - timedelta(days=1)
    _usage[caller] = [t for t in _usage[caller] if t > cutoff]
    if len(_usage[caller]) >= FREE_DAILY_LIMIT:
        return f"Free tier limit reached ({FREE_DAILY_LIMIT}/day). Upgrade to Pro: https://mcpize.com/csv-analytics-mcp/pro"
    _usage[caller].append(now)
    return None


# ---------------------------------------------------------------------------
# In-memory dataset store
# ---------------------------------------------------------------------------
_datasets: dict[str, "pd.DataFrame"] = {}


def _get_dataset(name: str):
    """Get a loaded dataset by name."""
    if name not in _datasets:
        raise KeyError(f"Dataset '{name}' not loaded. Use load_csv first. Loaded: {list(_datasets.keys())}")
    return _datasets[name]


def _df_to_dict(df, limit: int = 100) -> dict:
    """Convert a DataFrame to a JSON-safe dictionary with row limit."""
    import pandas as pd
    total = len(df)
    truncated = total > limit
    df_limited = df.head(limit)

    # Convert to records, handling special types
    records = []
    for _, row in df_limited.iterrows():
        record = {}
        for col in df_limited.columns:
            val = row[col]
            if pd.isna(val):
                record[col] = None
            elif isinstance(val, (datetime)):
                record[col] = val.isoformat()
            elif hasattr(val, 'item'):  # numpy types
                record[col] = val.item()
            else:
                record[col] = val
            # Ensure JSON-serializable
            try:
                json.dumps(record[col])
            except (TypeError, ValueError):
                record[col] = str(val)
        records.append(record)

    return {
        "columns": list(df_limited.columns),
        "rows": records,
        "row_count": len(records),
        "total_rows": total,
        "truncated": truncated,
    }


# ---------------------------------------------------------------------------
# Core operations
# ---------------------------------------------------------------------------

def _load_csv(file_path: str, name: str = "", delimiter: str = ",", encoding: str = "utf-8") -> dict:
    """Load a CSV file into memory."""
    import pandas as pd

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    df = pd.read_csv(file_path, delimiter=delimiter, encoding=encoding)
    dataset_name = name or os.path.splitext(os.path.basename(file_path))[0]
    _datasets[dataset_name] = df

    return {
        "status": "loaded",
        "name": dataset_name,
        "file": file_path,
        "rows": len(df),
        "columns": list(df.columns),
        "column_count": len(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "memory_mb": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
        "preview": _df_to_dict(df, limit=5),
    }


def _query_data(name: str, filter_expr: str = "", columns: Optional[list[str]] = None,
                sort_by: str = "", ascending: bool = True, limit: int = 100) -> dict:
    """Query a loaded dataset with filtering, column selection, and sorting."""
    import pandas as pd
    df = _get_dataset(name)

    # Apply filter
    if filter_expr:
        try:
            df = df.query(filter_expr)
        except Exception as e:
            return {"error": f"Invalid filter expression: {e}. Use pandas query syntax, e.g. 'age > 30 and city == \"London\"'"}

    # Select columns
    if columns:
        missing = [c for c in columns if c not in df.columns]
        if missing:
            return {"error": f"Columns not found: {missing}. Available: {list(df.columns)}"}
        df = df[columns]

    # Sort
    if sort_by:
        if sort_by not in df.columns:
            return {"error": f"Sort column '{sort_by}' not found. Available: {list(df.columns)}"}
        df = df.sort_values(sort_by, ascending=ascending)

    result = _df_to_dict(df, limit=limit)
    result["dataset"] = name
    result["filter"] = filter_expr
    return result


def _describe_columns(name: str) -> dict:
    """Get statistical summary of all columns."""
    import pandas as pd
    df = _get_dataset(name)

    stats = {}
    for col in df.columns:
        col_stats = {"dtype": str(df[col].dtype), "non_null": int(df[col].count()), "null_count": int(df[col].isna().sum())}

        if pd.api.types.is_numeric_dtype(df[col]):
            desc = df[col].describe()
            col_stats.update({
                "mean": round(float(desc.get("mean", 0)), 4),
                "std": round(float(desc.get("std", 0)), 4),
                "min": float(desc.get("min", 0)),
                "max": float(desc.get("max", 0)),
                "median": round(float(df[col].median()), 4),
                "25%": float(desc.get("25%", 0)),
                "75%": float(desc.get("75%", 0)),
            })
        else:
            col_stats["unique"] = int(df[col].nunique())
            top_values = df[col].value_counts().head(5)
            col_stats["top_values"] = {str(k): int(v) for k, v in top_values.items()}

        stats[col] = col_stats

    return {
        "dataset": name,
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "columns": stats,
    }


def _aggregate(name: str, group_by: list[str], metrics: dict[str, str]) -> dict:
    """Aggregate data with GROUP BY and aggregate functions.

    metrics: {"column_name": "agg_function"} where agg_function is one of:
    sum, mean, min, max, count, median, std, first, last
    """
    import pandas as pd
    df = _get_dataset(name)

    # Validate columns
    for col in group_by:
        if col not in df.columns:
            return {"error": f"Group column '{col}' not found. Available: {list(df.columns)}"}
    for col in metrics:
        if col not in df.columns:
            return {"error": f"Metric column '{col}' not found. Available: {list(df.columns)}"}

    valid_aggs = {"sum", "mean", "min", "max", "count", "median", "std", "first", "last", "nunique"}
    for col, agg in metrics.items():
        if agg not in valid_aggs:
            return {"error": f"Invalid aggregation '{agg}' for '{col}'. Use: {valid_aggs}"}

    result_df = df.groupby(group_by, as_index=False).agg(metrics)

    # Flatten multi-level column names if needed
    if isinstance(result_df.columns, pd.MultiIndex):
        result_df.columns = ['_'.join(col).strip('_') for col in result_df.columns]

    result = _df_to_dict(result_df, limit=200)
    result["dataset"] = name
    result["group_by"] = group_by
    result["metrics"] = metrics
    return result


def _export_chart_data(name: str, x_column: str, y_columns: list[str],
                       chart_type: str = "bar", limit: int = 50) -> dict:
    """Export data in a chart-ready format for visualization."""
    import pandas as pd
    df = _get_dataset(name)

    all_cols = [x_column] + y_columns
    missing = [c for c in all_cols if c not in df.columns]
    if missing:
        return {"error": f"Columns not found: {missing}. Available: {list(df.columns)}"}

    chart_df = df[all_cols].head(limit).dropna()

    labels = chart_df[x_column].astype(str).tolist()
    datasets = []
    for y_col in y_columns:
        values = chart_df[y_col].tolist()
        # Ensure numeric
        clean_values = []
        for v in values:
            try:
                clean_values.append(float(v))
            except (TypeError, ValueError):
                clean_values.append(0)
        datasets.append({
            "label": y_col,
            "data": clean_values,
        })

    return {
        "chart_type": chart_type,
        "labels": labels,
        "datasets": datasets,
        "data_points": len(labels),
        "dataset": name,
        "note": "Compatible with Chart.js, Plotly, or any charting library",
    }


def _pivot_table(name: str, index: str, columns: str, values: str,
                 aggfunc: str = "mean") -> dict:
    """Create a pivot table from a dataset."""
    import pandas as pd
    df = _get_dataset(name)

    for col in [index, columns, values]:
        if col not in df.columns:
            return {"error": f"Column '{col}' not found. Available: {list(df.columns)}"}

    valid_aggs = {"mean", "sum", "count", "min", "max", "median", "std"}
    if aggfunc not in valid_aggs:
        return {"error": f"Invalid aggfunc '{aggfunc}'. Use: {valid_aggs}"}

    try:
        pivot = pd.pivot_table(
            df, values=values, index=index, columns=columns,
            aggfunc=aggfunc, fill_value=0)
    except Exception as e:
        return {"error": f"Pivot table error: {e}"}

    # Convert to serializable format
    pivot_dict = {}
    for idx_val in pivot.index[:50]:  # Limit rows
        row_data = {}
        for col_val in pivot.columns[:20]:  # Limit columns
            val = pivot.loc[idx_val, col_val]
            try:
                row_data[str(col_val)] = round(float(val), 4) if val != 0 else 0
            except (TypeError, ValueError):
                row_data[str(col_val)] = str(val)
        pivot_dict[str(idx_val)] = row_data

    return {
        "dataset": name,
        "index": index,
        "columns_field": columns,
        "values_field": values,
        "aggfunc": aggfunc,
        "row_count": len(pivot_dict),
        "column_values": [str(c) for c in pivot.columns[:20]],
        "pivot": pivot_dict,
    }


# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------
mcp = FastMCP(
    "CSV Analytics MCP",
    instructions="Spreadsheet and CSV analysis toolkit: load files, filter/query data, compute statistics, create aggregations, pivot tables, and export chart-ready data. By MEOK AI Labs.")


@mcp.tool()
def load_csv(file_path: str, name: str = "", delimiter: str = ",", encoding: str = "utf-8") -> dict:
    """Load a CSV file into memory for analysis. The dataset is stored under
    a name (defaults to filename) and can be referenced in subsequent calls.

    Args:
        file_path: Absolute path to the CSV file
        name: Optional name for the dataset (default: filename without extension)
        delimiter: Column delimiter (default: comma)
        encoding: File encoding (default: utf-8)
    """
    err = _check_rate_limit()
    if err:
        return {"error": err}
    try:
        return _load_csv(file_path, name, delimiter, encoding)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def query_data(name: str, filter_expr: str = "", columns: Optional[list[str]] = None,
               sort_by: str = "", ascending: bool = True, limit: int = 100) -> dict:
    """Query a loaded dataset with filtering, column selection, and sorting.

    Uses pandas query syntax for filters:
    - 'age > 30'
    - 'city == "London" and salary > 50000'
    - 'status.isin(["active", "pending"])'

    Args:
        name: Dataset name (from load_csv)
        filter_expr: Pandas query expression for filtering rows
        columns: List of column names to return (default: all)
        sort_by: Column name to sort by
        ascending: Sort order (default: True)
        limit: Max rows to return (default: 100)
    """
    err = _check_rate_limit()
    if err:
        return {"error": err}
    try:
        return _query_data(name, filter_expr, columns, sort_by, ascending, min(limit, 500))
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def describe_columns(name: str) -> dict:
    """Get detailed statistics for every column in a dataset:
    - Numeric columns: mean, std, min, max, median, quartiles
    - Categorical columns: unique count, top 5 values with frequencies

    Args:
        name: Dataset name (from load_csv)
    """
    err = _check_rate_limit()
    if err:
        return {"error": err}
    try:
        return _describe_columns(name)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def aggregate(name: str, group_by: list[str], metrics: dict[str, str]) -> dict:
    """Aggregate data with GROUP BY and compute metrics.

    Supported aggregation functions: sum, mean, min, max, count, median, std, first, last, nunique

    Args:
        name: Dataset name (from load_csv)
        group_by: List of columns to group by (e.g. ["department", "year"])
        metrics: Dict of column -> aggregation function (e.g. {"salary": "mean", "id": "count"})
    """
    err = _check_rate_limit()
    if err:
        return {"error": err}
    try:
        return _aggregate(name, group_by, metrics)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def export_chart_data(name: str, x_column: str, y_columns: list[str],
                      chart_type: str = "bar", limit: int = 50) -> dict:
    """Export data in a chart-ready format. Output is compatible with Chart.js,
    Plotly, or any visualization library. Includes labels and datasets arrays.

    Args:
        name: Dataset name (from load_csv)
        x_column: Column for the X axis / labels
        y_columns: List of columns for Y axis / data series
        chart_type: Suggested chart type (bar, line, scatter, pie)
        limit: Max data points (default: 50)
    """
    err = _check_rate_limit()
    if err:
        return {"error": err}
    try:
        return _export_chart_data(name, x_column, y_columns, chart_type, limit)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def pivot_table(name: str, index: str, columns: str, values: str,
                aggfunc: str = "mean") -> dict:
    """Create a pivot table from a dataset. Reshapes data by grouping rows
    and spreading column values, similar to Excel pivot tables.

    Args:
        name: Dataset name (from load_csv)
        index: Column to use as row labels
        columns: Column whose unique values become new columns
        values: Column to aggregate
        aggfunc: Aggregation function (mean, sum, count, min, max, median, std)
    """
    err = _check_rate_limit()
    if err:
        return {"error": err}
    try:
        return _pivot_table(name, index, columns, values, aggfunc)
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    mcp.run()
