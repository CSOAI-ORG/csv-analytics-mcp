# CSV Analytics MCP Server
**By MEOK AI Labs** | [meok.ai](https://meok.ai)

Spreadsheet and CSV analysis toolkit for AI agents. Load CSV files, filter and query data, compute statistics, create aggregations, build pivot tables, and export chart-ready data -- all powered by pandas.

## Tools

| Tool | Description |
|------|-------------|
| `load_csv` | Load a CSV file into memory for analysis |
| `query_data` | Filter, select columns, sort, and slice data |
| `describe_columns` | Statistical summary (mean, std, quartiles, top values) |
| `aggregate` | GROUP BY with sum, mean, count, median, etc. |
| `export_chart_data` | Export data in Chart.js / Plotly compatible format |
| `pivot_table` | Excel-style pivot tables |

## Installation

```bash
pip install mcp pandas
```

## Usage

### Run the server

```bash
python server.py
```

### Claude Desktop config

```json
{
  "mcpServers": {
    "csv-analytics": {
      "command": "python",
      "args": ["/path/to/csv-analytics-mcp/server.py"]
    }
  }
}
```

### Workflow

1. **Load** a CSV file (stored in memory by name)
2. **Explore** with `describe_columns`
3. **Query** with filters, sorting, column selection
4. **Aggregate** or **pivot** for summaries
5. **Export** chart-ready data for visualization

### Example calls

**Load a CSV file:**
```
Tool: load_csv
Input: {"file_path": "/Users/me/data/sales.csv"}
Output: {"name": "sales", "rows": 15432, "columns": ["date", "product", "region", "amount", "quantity"], "dtypes": {"amount": "float64", "quantity": "int64"}}
```

**Describe columns:**
```
Tool: describe_columns
Input: {"name": "sales"}
Output: {"columns": {"amount": {"mean": 245.32, "std": 89.10, "min": 5.00, "max": 2500.00, "median": 210.50}, "region": {"unique": 4, "top_values": {"North": 4210, "South": 3890, ...}}}}
```

**Query with filters:**
```
Tool: query_data
Input: {"name": "sales", "filter_expr": "amount > 500 and region == 'North'", "sort_by": "amount", "ascending": false, "limit": 10}
Output: {"rows": [...], "row_count": 10, "total_rows": 312}
```

**Aggregate:**
```
Tool: aggregate
Input: {"name": "sales", "group_by": ["region"], "metrics": {"amount": "sum", "quantity": "mean"}}
Output: {"rows": [{"region": "North", "amount": 1234567.89, "quantity": 12.3}, ...]}
```

**Pivot table:**
```
Tool: pivot_table
Input: {"name": "sales", "index": "region", "columns": "product", "values": "amount", "aggfunc": "sum"}
Output: {"pivot": {"North": {"Widget A": 50000, "Widget B": 32000}, "South": {"Widget A": 45000, ...}}}
```

**Export for charting:**
```
Tool: export_chart_data
Input: {"name": "sales", "x_column": "region", "y_columns": ["amount"], "chart_type": "bar"}
Output: {"chart_type": "bar", "labels": ["North", "South", "East", "West"], "datasets": [{"label": "amount", "data": [1234567, 987654, ...]}]}
```

## Pricing

| Tier | Limit | Price |
|------|-------|-------|
| Free | 30 calls/day, 500 rows max per query | $0 |
| Pro | Unlimited + Excel/Parquet support + multi-file joins | $9/mo |
| Enterprise | Custom + streaming large files + scheduled reports | Contact us |

## License

MIT
