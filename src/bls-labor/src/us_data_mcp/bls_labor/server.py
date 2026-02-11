"""Bureau of Labor Statistics (BLS) MCP Server.

This server provides MCP tools for accessing BLS labor market and economic data.
"""

import asyncio
import json
from typing import Any, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .api_client import BLSAPIClient
from .models import BLSSeriesRequest, COMMON_SERIES


# Initialize MCP server
app = Server("us-data-mcp.bls-labor")

# Global API client
bls_client: Optional[BLSAPIClient] = None


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools for BLS data access."""
    return [
        Tool(
            name="get_series_data",
            description=(
                "Fetch data for one or more BLS series IDs. Returns time-series data "
                "including observations, periods, and values."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "series_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of series IDs (e.g., ['LNS14000000'] for national unemployment)"
                    },
                    "start_year": {
                        "type": "integer",
                        "description": "Start year (e.g., 2020)"
                    },
                    "end_year": {
                        "type": "integer",
                        "description": "End year (e.g., 2023)"
                    }
                },
                "required": ["series_ids"]
            }
        ),
        Tool(
            name="get_common_series",
            description=(
                "Get a list of commonly used BLS series IDs (unemployment, CPI, etc.) "
                "to help you formulate data requests."
            ),
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls for BLS operations."""
    global bls_client
    
    try:
        if bls_client is None:
            bls_client = BLSAPIClient()
            
        if name == "get_series_data":
            request = BLSSeriesRequest(**arguments)
            response = await bls_client.get_series_data(
                series_ids=request.series_ids,
                start_year=request.start_year,
                end_year=request.end_year
            )
            return [TextContent(type="text", text=json.dumps(response.model_dump(), indent=2))]
            
        elif name == "get_common_series":
            series = await bls_client.get_common_series()
            return [TextContent(type="text", text=json.dumps({"common_series": series}, indent=2))]
            
        else:
            return [TextContent(type="text", text=json.dumps({"success": False, "error": f"Unknown tool: {name}"}, indent=2))]
            
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"success": False, "error": str(e)}, indent=2))]


async def main():
    """Main entry point for the BLS MCP server."""
    global bls_client
    try:
        bls_client = BLSAPIClient()
        async with stdio_server() as (read_stream, write_stream):
            await app.run(read_stream, write_stream, app.create_initialization_options())
    finally:
        if bls_client:
            await bls_client.close()


if __name__ == "__main__":
    asyncio.run(main())
