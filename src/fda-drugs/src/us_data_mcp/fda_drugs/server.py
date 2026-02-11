"""US FDA Drugs MCP Server.

This server provides MCP tools for accessing FDA drug information, recalls, and adverse events.
"""

import asyncio
import json
from typing import Any, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .api_client import FDAAPIClient
from .models import (
    DrugSearchRequest,
    RecallSearchRequest,
    AdverseEventRequest,
    DeviceSearchRequest,
    AllRecallSearchRequest,
    RECALL_CLASSIFICATIONS,
    COMMON_ADVERSE_REACTIONS
)


# Initialize MCP server
app = Server("us-data-mcp.fda-drugs")

# Global API client
fda_client: Optional[FDAAPIClient] = None


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools for FDA data access."""
    return [
        Tool(
            name="search_drugs",
            description=(
                "Search FDA-approved drugs by brand name, generic name, or application number. "
                "Returns drug approval information, manufacturer, and regulatory details."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "brand_name": {
                        "type": "string",
                        "description": "Brand/trade name of the drug (e.g., 'Lipitor')"
                    },
                    "generic_name": {
                        "type": "string",
                        "description": "Generic/chemical name (e.g., 'atorvastatin')"
                    },
                    "application_number": {
                        "type": "string",
                        "description": "FDA application number"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results (default: 10)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 100
                    }
                }
            }
        ),
        Tool(
            name="search_drug_labels",
            description=(
                "Search drug labeling information including indications, dosage, warnings, "
                "and adverse reactions from official FDA-approved labels."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "brand_name": {
                        "type": "string",
                        "description": "Brand name of the drug"
                    },
                    "generic_name": {
                        "type": "string",
                        "description": "Generic name of the drug"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results (default: 10)",
                        "default": 10
                    }
                }
            }
        ),
        Tool(
            name="search_recalls",
            description=(
                "Search drug recalls and safety alerts. Filter by classification "
                "(Class I=most serious, Class III=least serious) and status."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "product_description": {
                        "type": "string",
                        "description": "Product description or drug name"
                    },
                    "classification": {
                        "type": "string",
                        "description": "Recall classification: I, II, or III",
                        "enum": ["I", "II", "III"]
                    },
                    "status": {
                        "type": "string",
                        "description": "Recall status: Ongoing, Completed, or Terminated"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results (default: 10)",
                        "default": 10
                    }
                }
            }
        ),
        Tool(
            name="search_adverse_events",
            description=(
                "Search adverse event reports for a drug. Returns patient reactions "
                "and side effects reported to the FDA."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "drug_name": {
                        "type": "string",
                        "description": "Drug name to search for adverse events"
                    },
                    "reaction": {
                        "type": "string",
                        "description": "Specific adverse reaction/side effect (optional)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results (default: 10)",
                        "default": 10
                    }
                },
                "required": ["drug_name"]
            }
        ),
        Tool(
            name="get_recall_classifications",
            description=(
                "Get FDA recall classification definitions (Class I, II, III) "
                "to understand recall severity levels."
            ),
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="search_devices",
            description=(
                "Search for FDA-regulated medical devices by name. "
                "Returns 510(k) clearance information and manufacturer details."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "device_name": {
                        "type": "string",
                        "description": "Name of the medical device"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max results",
                        "default": 10
                    }
                },
                "required": ["device_name"]
            }
        ),
        Tool(
            name="search_all_recalls",
            description=(
                "Search all FDA recalls including food, medical devices, and veterinary products. "
                "Filter by category and product description."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Category: food, device, or drug",
                        "enum": ["food", "device", "drug"]
                    },
                    "product_description": {
                        "type": "string",
                        "description": "Product name or keywords"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max results",
                        "default": 10
                    }
                },
                "required": ["category"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls for FDA operations."""
    global fda_client
    
    try:
        # Initialize client if needed
        if fda_client is None:
            fda_client = FDAAPIClient()
        
        if name == "search_drugs":
            request = DrugSearchRequest(**arguments)
            response = await fda_client.search_drugs(
                brand_name=request.brand_name,
                generic_name=request.generic_name,
                application_number=request.application_number,
                limit=request.limit
            )
            return [TextContent(type="text", text=json.dumps(response.model_dump(), indent=2))]
        
        elif name == "search_drug_labels":
            response = await fda_client.search_drug_labels(
                brand_name=arguments.get("brand_name"),
                generic_name=arguments.get("generic_name"),
                limit=arguments.get("limit", 10)
            )
            return [TextContent(type="text", text=json.dumps(response.model_dump(), indent=2))]
        
        elif name == "search_recalls":
            request = RecallSearchRequest(**arguments)
            response = await fda_client.search_recalls(
                product_description=request.product_description,
                classification=request.classification,
                status=request.status,
                limit=request.limit
            )
            return [TextContent(type="text", text=json.dumps(response.model_dump(), indent=2))]
        
        elif name == "search_adverse_events":
            request = AdverseEventRequest(**arguments)
            response = await fda_client.search_adverse_events(
                drug_name=request.drug_name,
                reaction=request.reaction,
                limit=request.limit
            )
            return [TextContent(type="text", text=json.dumps(response.model_dump(), indent=2))]
        
        elif name == "get_recall_classifications":
            return [TextContent(
                type="text",
                text=json.dumps({
                    "classifications": RECALL_CLASSIFICATIONS,
                    "common_reactions": COMMON_ADVERSE_REACTIONS,
                    "usage": "Use classification codes (I, II, III) in search_recalls"
                }, indent=2)
            )]
        
        elif name == "search_devices":
            request = DeviceSearchRequest(**arguments)
            response = await fda_client.search_devices(request.device_name, request.limit)
            return [TextContent(type="text", text=json.dumps(response.model_dump(), indent=2))]

        elif name == "search_all_recalls":
            request = AllRecallSearchRequest(**arguments)
            response = await fda_client.search_all_recalls(request.category, request.product_description, request.limit)
            return [TextContent(type="text", text=json.dumps(response.model_dump(), indent=2))]
        
        else:
            return [TextContent(
                type="text",
                text=json.dumps({"success": False, "error": f"Unknown tool: {name}"}, indent=2)
            )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({"success": False, "error": f"Error: {str(e)}"}, indent=2)
        )]


async def main():
    """Main entry point for the FDA MCP server."""
    global fda_client
    
    try:
        fda_client = FDAAPIClient()
        async with stdio_server() as (read_stream, write_stream):
            await app.run(read_stream, write_stream, app.create_initialization_options())
    finally:
        if fda_client:
            await fda_client.close()


if __name__ == "__main__":
    asyncio.run(main())
