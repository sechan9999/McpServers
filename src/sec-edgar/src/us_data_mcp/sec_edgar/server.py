"""US SEC EDGAR MCP Server.

This server provides MCP tools for accessing SEC EDGAR company filings and financial data.
"""

import asyncio
import json
from typing import Any, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .api_client import SECAPIClient
from .models import CompanySearchRequest, FilingsRequest, COMMON_FORM_TYPES


# Initialize MCP server
app = Server("us-data-mcp.sec-edgar")

# Global API client
sec_client: Optional[SECAPIClient] = None


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools for SEC EDGAR access.
    
    Returns:
        List of available tools
    """
    return [
        Tool(
            name="search_company",
            description=(
                "Search for companies in SEC EDGAR database by name, ticker symbol, or CIK. "
                "Returns company information including CIK, name, ticker, and exchange."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Company name, ticker symbol (e.g., 'AAPL'), or CIK number"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_company_filings",
            description=(
                "Get SEC filings for a company by CIK. Returns recent filings with links. "
                "Can filter by form type (10-K, 10-Q, 8-K, etc.)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "cik": {
                        "type": "string",
                        "description": "Company CIK (Central Index Key) - can be any length, will be normalized"
                    },
                    "form_type": {
                        "type": "string",
               "description": "Optional: Filter by form type (10-K, 10-Q, 8-K, DEF 14A, etc.)"
                    },
                    "count": {
                        "type": "integer",
                        "description": "Number of filings to retrieve (default: 10, max: 100)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 100
                    }
                },
                "required": ["cik"]
            }
        ),
        Tool(
            name="get_company_facts",
            description=(
                "Get company financial facts (XBRL data) from SEC. "
                "Returns structured financial statement data including revenue, assets, liabilities, etc."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "cik": {
                        "type": "string",
                        "description": "Company CIK (Central Index Key)"
                    }
                },
                "required": ["cik"]
            }
        ),
        Tool(
            name="get_form_types",
            description=(
                "Get a reference list of common SEC form types and their descriptions. "
                "Helps identify which form types to use when searching filings."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls for SEC EDGAR operations.
    
    Args:
        name: Tool name
        arguments: Tool arguments
        
    Returns:
        List of text content responses
    """
    global sec_client
    
    try:
        if name == "search_company":
            # Validate request
            try:
                request = CompanySearchRequest(**arguments)
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": f"Invalid parameters: {str(e)}"
                    }, indent=2)
                )]
            
            # Initialize client if needed
            if sec_client is None:
                sec_client = SECAPIClient()
            
            # Search for company
            response = await sec_client.search_company(request.query)
            
            return [TextContent(
                type="text",
                text=json.dumps(response.model_dump(), indent=2)
            )]
        
        elif name == "get_company_filings":
            # Validate request
            try:
                request = FilingsRequest(**arguments)
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": f"Invalid parameters: {str(e)}"
                    }, indent=2)
                )]
            
            # Initialize client if needed
            if sec_client is None:
                sec_client = SECAPIClient()
            
            # Get filings
            response = await sec_client.get_company_filings(
                cik=request.cik,
                form_type=request.form_type,
                count=request.count
            )
            
            return [TextContent(
                type="text",
                text=json.dumps(response.model_dump(), indent=2)
            )]
        
        elif name == "get_company_facts":
            # Get CIK from arguments
            cik = arguments.get("cik")
            if not cik:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": "CIK is required"
                    }, indent=2)
                )]
            
            # Initialize client if needed
            if sec_client is None:
                sec_client = SECAPIClient()
            
            # Get company facts
            response = await sec_client.get_company_facts(cik)
            
            return [TextContent(
                type="text",
                text=json.dumps(response.model_dump(), indent=2)
            )]
        
        elif name == "get_form_types":
            # Return form types reference
            form_types_grouped = {
                "Annual & Quarterly Reports": {
                    k: v for k, v in COMMON_FORM_TYPES.items()
                    if any(x in k for x in ["10-K", "10-Q", "8-K"])
                },
                "Registration & Offerings": {
                    k: v for k, v in COMMON_FORM_TYPES.items()
                    if k.startswith("S-") or "424" in k
                },
                "Proxy Materials": {
                    k: v for k, v in COMMON_FORM_TYPES.items()
                    if "14A" in k
                },
                "Ownership Reports": {
                    k: v for k, v in COMMON_FORM_TYPES.items()
                    if k in ["3", "4", "5", "13F-HR", "13D", "13G"]
                },
                "Foreign Companies": {
                    k: v for k, v in COMMON_FORM_TYPES.items()
                    if k in ["20-F", "6-K"]
                }
            }
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "form_types": form_types_grouped,
                    "all_types": COMMON_FORM_TYPES,
                    "usage": "Use these form type codes in the 'form_type' parameter of get_company_filings"
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
    """Main entry point for the SEC EDGAR MCP server."""
    global sec_client
    
    try:
        # Initialize SEC API client (no API key needed)
        sec_client = SECAPIClient()
        
        # Run server
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    finally:
        # Cleanup
        if sec_client:
            await sec_client.close()


if __name__ == "__main__":
    asyncio.run(main())
