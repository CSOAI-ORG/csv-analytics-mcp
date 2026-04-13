# CSV Analytics MCP Server

> **By [MEOK AI Labs](https://meok.ai)** — Sovereign AI tools for everyone.

Spreadsheet and CSV analysis toolkit for AI agents. Load CSV files, filter and query data, compute statistics, create aggregations, build pivot tables, and export chart-ready data -- all powered by pandas.

[![MCPize](https://img.shields.io/badge/MCPize-Listed-blue)](https://mcpize.com/mcp/csv-analytics)
[![MIT License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-255+_servers-purple)](https://meok.ai)

## Tools

| Tool | Description |
|------|-------------|
| `load_csv` | Load a CSV file into memory for analysis |
| `query_data` | Query a dataset with filtering, column selection, and sorting |
| `describe_columns` | Get detailed statistics for every column |
| `aggregate` | Aggregate data with GROUP BY and compute metrics |
| `export_chart_data` | Export data in a chart-ready format (Chart.js compatible) |
| `pivot_table` | Create a pivot table from a dataset |

## Quick Start

```bash
pip install mcp
git clone https://github.com/CSOAI-ORG/csv-analytics-mcp.git
cd csv-analytics-mcp
python server.py
```

## Claude Desktop Config

```json
{
  "mcpServers": {
    "csv-analytics": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "/path/to/csv-analytics-mcp"
    }
  }
}
```

## Pricing

| Plan | Price | Requests |
|------|-------|----------|
| Free | $0/mo | 30 calls/day, 500 rows max |
| Pro | $9/mo | Unlimited + Excel/Parquet + multi-file joins |
| Enterprise | Contact us | Custom + streaming + scheduled reports |

[Get on MCPize](https://mcpize.com/mcp/csv-analytics)

## Part of MEOK AI Labs

This is one of 255+ MCP servers by MEOK AI Labs. Browse all at [meok.ai](https://meok.ai) or [GitHub](https://github.com/CSOAI-ORG).

---
**MEOK AI Labs** | [meok.ai](https://meok.ai) | nicholas@meok.ai | United Kingdom
