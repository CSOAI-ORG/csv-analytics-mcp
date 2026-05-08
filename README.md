<div align="center">

# Csv Analytics MCP

**MCP server for csv analytics mcp operations**

[![PyPI](https://img.shields.io/pypi/v/meok-csv-analytics-mcp)](https://pypi.org/project/meok-csv-analytics-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-MCP_Server-purple)](https://meok.ai)

</div>

## Overview

Csv Analytics MCP provides AI-powered tools via the Model Context Protocol (MCP).

## Tools

| Tool | Description |
|------|-------------|
| `load_csv` | Load a CSV file into memory for analysis. The dataset is stored under |
| `query_data` | Query a loaded dataset with filtering, column selection, and sorting. |
| `describe_columns` | Get detailed statistics for every column in a dataset: |
| `aggregate` | Aggregate data with GROUP BY and compute metrics. |
| `export_chart_data` | Export data in a chart-ready format. Output is compatible with Chart.js, |
| `pivot_table` | Create a pivot table from a dataset. Reshapes data by grouping rows |

## Installation

```bash
pip install meok-csv-analytics-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "csv-analytics-mcp": {
      "command": "python",
      "args": ["-m", "meok_csv_analytics_mcp.server"]
    }
  }
}
```

## Usage with FastMCP

```python
from mcp.server.fastmcp import FastMCP

# This server exposes 6 tool(s) via MCP
# See server.py for full implementation
```

## License

MIT © [MEOK AI Labs](https://meok.ai)
