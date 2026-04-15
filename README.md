# CSV Analytics MCP Server

> By [MEOK AI Labs](https://meok.ai) — Spreadsheet and CSV analysis toolkit with queries, statistics, pivot tables, and chart export

## Installation

```bash
pip install csv-analytics-mcp pandas
```

## Usage

```bash
python server.py
```

## Tools

### `load_csv`
Load a CSV file into memory for analysis. Returns schema, preview, and memory usage.

**Parameters:**
- `file_path` (str): Absolute path to the CSV file
- `name` (str): Dataset name (default: filename)
- `delimiter` (str): Column delimiter (default: comma)
- `encoding` (str): File encoding (default: utf-8)

### `query_data`
Query a loaded dataset with pandas query syntax, column selection, and sorting.

**Parameters:**
- `name` (str): Dataset name
- `filter_expr` (str): Pandas query expression (e.g., 'age > 30 and city == "London"')
- `columns` (list[str]): Columns to return
- `sort_by` (str): Sort column
- `ascending` (bool): Sort order
- `limit` (int): Max rows (default 100)

### `describe_columns`
Get detailed statistics for every column (mean, std, quartiles for numeric; top values for categorical).

**Parameters:**
- `name` (str): Dataset name

### `aggregate`
Aggregate data with GROUP BY and compute metrics (sum, mean, min, max, count, median, std, nunique).

**Parameters:**
- `name` (str): Dataset name
- `group_by` (list[str]): Columns to group by
- `metrics` (dict[str, str]): Column to aggregation function mapping

### `export_chart_data`
Export data in a chart-ready format compatible with Chart.js, Plotly, or any charting library.

**Parameters:**
- `name` (str): Dataset name
- `x_column` (str): X axis column
- `y_columns` (list[str]): Y axis columns
- `chart_type` (str): Chart type (bar, line, scatter, pie)
- `limit` (int): Max data points (default 50)

### `pivot_table`
Create a pivot table similar to Excel pivot tables.

**Parameters:**
- `name` (str): Dataset name
- `index` (str): Row labels column
- `columns` (str): Column values column
- `values` (str): Values column
- `aggfunc` (str): Aggregation function (mean, sum, count, min, max)

## Authentication

Free tier: 30 calls/day. Upgrade at [meok.ai/pricing](https://meok.ai/pricing) for unlimited access.

## License

MIT — MEOK AI Labs
