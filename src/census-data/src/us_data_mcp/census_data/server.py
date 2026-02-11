"""US Census Bureau Data MCP Server.

This server provides MCP tools for accessing US Census Bureau data through the Census API.
"""

import asyncio
import json
from typing import Any, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    EmbeddedResource,
    ImageContent,
    INVALID_PARAMS,
    INTERNAL_ERROR,
)

from .api_client import CensusAPIClient
from .models import PopulationSearchRequest, EconomicSearchRequest, COMMON_VARIABLES


# Initialize MCP server
app = Server("us-data-mcp.census-data")

# Global API client
census_client: Optional[CensusAPIClient] = None


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools for Census data access.
    
    Returns:
        List of available tools
    """
    return [
        Tool(
            name="search_population",
            description=(
                "Search US Census population data by geography. "
                "Returns population statistics including total population, median age, "
                "and other demographic data for states and counties."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "year": {
                        "type": "integer",
                        "description": "Year of census data (e.g., 2020, 2021)",
                        "minimum": 2000,
                        "maximum": 2030
                    },
                    "state": {
                        "type": "string",
                        "description": "State FIPS code (2 digits, e.g., '06' for California)",
                        "pattern": "^[0-9]{2}$"
                    },
                    "county": {
                        "type": "string",
                        "description": "County FIPS code (3 digits, optional)",
                        "pattern": "^[0-9]{3}$"
                    },
                    "variables": {
                        "type": "array",
                        "description": "List of census variable codes to retrieve",
                        "items": {"type": "string"},
                        "default": ["NAME", "B01001_001E", "B01002_001E"]
                    }
                },
                "required": ["year", "state"]
            }
        ),
        Tool(
            name="search_economic",
            description=(
                "Search US Census economic indicators data. "
                "Returns economic data including median household income, poverty rates, "
                "unemployment, and other economic indicators."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "year": {
                        "type": "integer",
                        "description": "Year of data",
                        "minimum": 2000,
                        "maximum": 2030
                    },
                    "dataset": {
                        "type": "string",
                        "description": "Dataset name (default: 'acs/acs5' for 5-year American Community Survey)",
                        "default": "acs/acs5"
                    },
                    "variables": {
                        "type": "array",
                        "description": "List of economic variable codes",
                        "items": {"type": "string"},
                        "default": ["NAME", "B19013_001E", "B17001_002E", "B23025_005E"]
                    },
                    "geography": {
                        "type": "string",
                        "description": "Geographic level (e.g., 'state:*', 'county:*')",
                        "default": "state:*"
                    },
                    "state": {
                        "type": "string",
                        "description": "State FIPS code filter (2 digits, optional)",
                        "pattern": "^[0-9]{2}$"
                    }
                },
                "required": ["year"]
            }
        ),
        Tool(
            name="get_common_variables",
            description=(
                "Get a reference list of commonly used Census variables with their descriptions. "
                "This helps identify which variables to use in population and economic searches."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_state_fips",
            description=(
                "Get FIPS codes for US states. Returns a mapping of state names to their "
                "2-digit FIPS codes used in Census API queries."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "state_name": {
                        "type": "string",
                        "description": "State name to look up (optional, returns all if not provided)"
                    }
                },
                "required": []
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls for Census data operations.
    
    Args:
        name: Tool name
        arguments: Tool arguments
        
    Returns:
        List of text content responses
    """
    global census_client
    
    try:
        if name == "search_population":
            # Validate request
            try:
                request = PopulationSearchRequest(**arguments)
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": f"Invalid parameters: {str(e)}"
                    }, indent=2)
                )]
            
            # Get population data
            if census_client is None:
                census_client = CensusAPIClient()
            
            response = await census_client.get_population_data(
                year=request.year,
                state=request.state,
                county=request.county,
                variables=request.variables
            )
            
            return [TextContent(
                type="text",
                text=json.dumps(response.model_dump(), indent=2)
            )]
        
        elif name == "search_economic":
            # Validate request
            try:
                request = EconomicSearchRequest(**arguments)
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": f"Invalid parameters: {str(e)}"
                    }, indent=2)
                )]
            
            # Get economic data
            if census_client is None:
                census_client = CensusAPIClient()
            
            response = await census_client.get_economic_data(
                year=request.year,
                dataset=request.dataset,
                variables=request.variables,
                geography=request.geography,
                state=request.state
            )
            
            return [TextContent(
                type="text",
                text=json.dumps(response.model_dump(), indent=2)
            )]
        
        elif name == "get_common_variables":
            # Return common variables reference
            variables_by_category = {
                "Population": {k: v for k, v in COMMON_VARIABLES.items() if "Population" in v or "Age" in v},
                "Economic": {k: v for k, v in COMMON_VARIABLES.items() if any(word in v for word in ["Income", "Poverty", "Unemployment"])},
                "Housing": {k: v for k, v in COMMON_VARIABLES.items() if "Housing" in v or "Home" in v},
                "Education": {k: v for k, v in COMMON_VARIABLES.items() if any(word in v for word in ["Degree", "Bachelor", "Master", "Doctorate"])},
                "Demographics": {k: v for k, v in COMMON_VARIABLES.items() if any(word in v for word in ["White", "Black", "Asian", "Hispanic", "Indian"])}
            }
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "common_variables": variables_by_category,
                    "usage": "Use these variable codes in the 'variables' parameter of search_population or search_economic tools"
                }, indent=2)
            )]
        
        elif name == "get_state_fips":
            # Return state FIPS codes
            state_fips = {
                "Alabama": "01", "Alaska": "02", "Arizona": "04", "Arkansas": "05",
                "California": "06", "Colorado": "08", "Connecticut": "09", "Delaware": "10",
                "Florida": "12", "Georgia": "13", "Hawaii": "15", "Idaho": "16",
                "Illinois": "17", "Indiana": "18", "Iowa": "19", "Kansas": "20",
                "Kentucky": "21", "Louisiana": "22", "Maine": "23", "Maryland": "24",
                "Massachusetts": "25", "Michigan": "26", "Minnesota": "27", "Mississippi": "28",
                "Missouri": "29", "Montana": "30", "Nebraska": "31", "Nevada": "32",
                "New Hampshire": "33", "New Jersey": "34", "New Mexico": "35", "New York": "36",
                "North Carolina": "37", "North Dakota": "38", "Ohio": "39", "Oklahoma": "40",
                "Oregon": "41", "Pennsylvania": "42", "Rhode Island": "44", "South Carolina": "45",
                "South Dakota": "46", "Tennessee": "47", "Texas": "48", "Utah": "49",
                "Vermont": "50", "Virginia": "51", "Washington": "53", "West Virginia": "54",
                "Wisconsin": "55", "Wyoming": "56", "District of Columbia": "11",
                "Puerto Rico": "72"
            }
            
            state_name = arguments.get("state_name")
            if state_name:
                # Case-insensitive lookup
                for name, code in state_fips.items():
                    if name.lower() == state_name.lower():
                        return [TextContent(
                            type="text",
                            text=json.dumps({
                                "state": name,
                                "fips_code": code
                            }, indent=2)
                        )]
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": f"State '{state_name}' not found"
                    }, indent=2)
                )]
            else:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "state_fips_codes": state_fips
                    }, indent=2)
                )]
        
        else:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": f"Unknown tool: {name}"
                }, indent=2)
            )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": f"Error executing tool: {str(e)}"
            }, indent=2)
        )]


async def main():
    """Main entry point for the Census MCP server."""
    global census_client
    
    try:
        # Initialize Census API client
        census_client = CensusAPIClient()
        
        # Run server
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    finally:
        # Cleanup
        if census_client:
            await census_client.close()


if __name__ == "__main__":
    asyncio.run(main())
