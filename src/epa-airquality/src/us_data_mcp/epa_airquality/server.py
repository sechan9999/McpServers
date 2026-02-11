"""EPA Air Quality MCP Server.

This server provides MCP tools for accessing EPA Air Quality System (AQS) data.
"""

import asyncio
import json
from typing import Any, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .api_client import EPAAQSClient
from .models import AQSSearchRequest, COMMON_PARAMS


# Initialize MCP server
app = Server("us-data-mcp.epa-airquality")

# Global API client
epa_client: Optional[EPAAQSClient] = None


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools for EPA data access."""
    return [
        Tool(
            name="get_daily_air_quality",
            description=(
                "Fetch daily air quality summary data from EPA AQS. "
                "Requires parameter code, start date, end date, and state/county FIPS codes."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "param_code": {
                        "type": "string",
                        "description": "Parameter code (e.g., '44201' for Ozone, '88101' for PM2.5)"
                    },
                    "bdate": {
                        "type": "string",
                        "description": "Begin date (YYYYMMDD)"
                    },
                    "edate": {
                        "type": "string",
                        "description": "End date (YYYYMMDD)"
                    },
                    "state": {
                        "type": "string",
                        "description": "2-digit State FIPS code"
                    },
                    "county": {
                        "type": "string",
                        "description": "3-digit County FIPS code (optional)"
                    }
                },
                "required": ["param_code", "bdate", "edate", "state"]
            }
        ),
        Tool(
            name="get_common_aqs_parameters",
            description=(
                "Get a reference list of commonly used EPA AQS parameter codes "
                "for air pollutants like Ozone, PM2.5, SO2, etc."
            ),
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls for EPA operations."""
    global epa_client
    
    try:
        if epa_client is None:
            epa_client = EPAAQSClient()
            
        if name == "get_daily_air_quality":
            request = AQSSearchRequest(**arguments)
            response = await epa_client.get_daily_data(
                param_code=request.param_code,
                bdate=request.bdate,
                edate=request.edate,
                state=request.state,
                county=request.county
            )
            return [TextContent(type="text", text=json.dumps(response.model_dump(), indent=2))]
            
        elif name == "get_common_aqs_parameters":
            params = await epa_client.get_common_params()
            return [TextContent(type="text", text=json.dumps({"common_parameters": params}, indent=2))]
            
        else:
            return [TextContent(type="text", text=json.dumps({"success": False, "error": f"Unknown tool: {name}"}, indent=2))]
            
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"success": False, "error": str(e)}, indent=2))]


async def main():
    """Main entry point for the EPA MCP server."""
    global epa_client
    try:
        epa_client = EPAAQSClient()
        async with stdio_server() as (read_stream, write_stream):
            await app.run(read_stream, write_stream, app.create_initialization_options())
    finally:
        if epa_client:
            await epa_client.close()


if __name__ == "__main__":
    asyncio.run(main())
