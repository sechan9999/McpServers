# US Data.gov MCP Servers - Implementation Plan

## Project Overview

This project implements Model Context Protocol (MCP) servers to provide standardized access to US government public data APIs through AI tools like Claude Desktop and Cline. It's inspired by the Korean data.go.kr MCP servers project but adapted for US data sources.

## What is MCP?

Model Context Protocol (MCP) is an open protocol that enables seamless integration between LLM applications and external data sources and tools. MCP servers are lightweight programs that expose specific functionality through the protocol, allowing AI tools to communicate with various data sources in a standardized way.

## Why US Public Data MCP Servers?

The US government's data.gov portal provides access to thousands of datasets from various federal agencies through APIs. This project wraps these APIs as MCP servers to enable:

- **Standardized Access**: Unified MCP interface for diverse US government APIs
- **AI Tool Integration**: Direct access to public data from Claude, Cline, and other AI assistants
- **Easy Installation**: Simple setup via pip or uv
- **Type Safety**: Strong type validation using Pydantic
- **Developer Friendly**: Template-based rapid server creation

## Selected US Data Sources

Based on availability and usefulness, we'll implement MCP servers for:

### Phase 1 - Core Servers (Priority)

1. **Census Bureau API** (`us-data-mcp.census-data`)
   - Population demographics
   - Economic indicators
   - Housing statistics
   - Purpose: Demographic and economic analysis

2. **SEC EDGAR API** (`us-data-mcp.sec-edgar`)
   - Company filings (10-K, 10-Q, 8-K)
   - Financial statements
   - Insider trading information
   - Purpose: Business and financial analysis

3. **FDA Drug Information** (`us-data-mcp.fda-drugs`)
   - Drug approvals
   - Recalls and safety alerts
   - Product labeling
   - Purpose: Healthcare and pharmaceutical information

4. **BLS Labor Statistics** (`us-data-mcp.bls-labor`)
   - Employment data
   - Wage statistics
   - Inflation/CPI data
   - Purpose: Economic and labor market analysis

### Phase 2 - Extended Servers

5. **USA Spending API** (`us-data-mcp.usa-spending`)
   - Federal spending data
   - Contract awards
   - Grant information
   - Purpose: Government transparency and procurement analysis

6. **EPA Air Quality** (`us-data-mcp.epa-airquality`)
   - Air quality index
   - Pollutant measurements
   - Environmental monitoring
   - Purpose: Environmental health analysis

## Project Structure

```
us_data_mcp_servers/
├── README.md                      # Main documentation
├── IMPLEMENTATION_PLAN.md         # This file
├── CONTRIBUTING.md                # Contribution guidelines
├── TEMPLATE_USAGE.md             # Template documentation
├── pyproject.toml                # Project dependencies
├── uv.lock                       # Dependency lock file
├── scripts/
│   └── create_mcp_server.py      # Auto-generation script
├── template/                      # Cookiecutter template
│   ├── cookiecutter.json
│   └── {{cookiecutter.server_name}}/
│       ├── src/
│       ├── tests/
│       └── pyproject.toml
└── src/
    ├── census-data/              # Census Bureau MCP server
    │   ├── src/
    │   │   └── us_data_mcp/
    │   │       └── census_data/
    │   │           ├── __init__.py
    │   │           ├── server.py
    │   │           ├── models.py
    │   │           └── api_client.py
    │   ├── tests/
    │   └── pyproject.toml
    ├── sec-edgar/                # SEC EDGAR MCP server
    ├── fda-drugs/                # FDA Drug Info MCP server
    ├── bls-labor/                # BLS Labor Stats MCP server
    ├── usa-spending/             # USA Spending MCP server
    └── epa-airquality/           # EPA Air Quality MCP server
```

## Technical Architecture

### Core Components

Each MCP server will follow this architecture:

```
┌─────────────────────────────────────┐
│   AI Client (Claude/Cline)         │
└─────────────┬───────────────────────┘
              │ MCP Protocol
┌─────────────▼───────────────────────┐
│   MCP Server                        │
│   ├── Tool Definitions              │
│   ├── Request Handlers              │
│   └── Response Formatters           │
└─────────────┬───────────────────────┘
              │ HTTP/REST
┌─────────────▼───────────────────────┐
│   US Government API                 │
│   (data.gov, census.gov, etc.)      │
└─────────────────────────────────────┘
```

### Technology Stack

- **Python 3.11+**: Core language
- **MCP SDK**: Model Context Protocol implementation
- **FastMCP**: Simplified MCP server framework
- **Pydantic**: Data validation and type safety
- **httpx**: Modern async HTTP client
- **pytest**: Testing framework
- **UV**: Fast Python package installer

### Server Template Components

Each server will include:

1. **server.py**: Main MCP server implementation
   - Tool definitions
   - Request/response handling
   - Error management

2. **models.py**: Pydantic models
   - Request schemas
   - Response schemas
   - Data validation

3. **api_client.py**: API interaction layer
   - HTTP client setup
   - API key management
   - Rate limiting
   - Retry logic

4. **tests/**: Test suite
   - Unit tests
   - Integration tests
   - Mock API responses

## Implementation Steps

### Step 1: Project Setup ✓
- [x] Create project directory structure
- [x] Set up pyproject.toml with dependencies
- [x] Configure uv for dependency management
- [x] Create README.md with project overview
- [x] Set up git repository

### Step 2: Template Development

- [ ] Create cookiecutter template structure
- [ ] Define template variables (server name, API endpoint, etc.)
- [ ] Implement base server.py template
- [ ] Implement base models.py template
- [ ] Implement base api_client.py template
- [ ] Create test template
- [ ] Document template usage in TEMPLATE_USAGE.md

### Step 3: Automation Script

- [ ] Create create_mcp_server.py script
- [ ] Implement interactive prompts for server details
- [ ] Add validation for user inputs
- [ ] Generate boilerplate from template
- [ ] Auto-update pyproject.toml

### Step 4: Phase 1 Server Implementation ✓
#### Census Bureau Server ✓
- [x] Register for Census API key
- [x] Research Census API endpoints
- [x] Implement census-data server
- [x] Create Pydantic models for Census data
- [x] Write unit tests
- [x] Test with Claude Desktop
- [x] Document usage examples

#### SEC EDGAR Server ✓
- [x] Research SEC EDGAR API
- [x] Implement sec-edgar server
- [x] Create models for SEC filings
- [x] Write unit tests
- [x] Test with Claude Desktop
- [x] Document usage examples

#### FDA Drugs Server ✓
- [x] Research FDA API endpoints
- [x] Implement fda-drugs server
- [x] Create models for drug data
- [x] Write unit tests
- [x] Test with Claude Desktop
- [x] Document usage examples

#### BLS Labor Server ✓
- [x] Register for BLS API key
- [x] Research BLS API endpoints
- [x] Implement bls-labor server
- [x] Create models for labor data
- [x] Write unit tests
- [x] Test with Claude Desktop
- [x] Document usage examples

### Step 5: Documentation

- [ ] Write comprehensive README.md
- [ ] Create installation guide
- [ ] Document each server's tools and parameters
- [ ] Add configuration examples for Claude Desktop
- [ ] Add configuration examples for Cline
- [ ] Create CONTRIBUTING.md guide
- [ ] Add usage examples and tutorials

### Step 6: Testing & Quality Assurance

- [ ] Run pytest on all servers
- [ ] Test integration with Claude Desktop
- [ ] Test integration with Cline
- [ ] Validate error handling
- [ ] Check rate limiting behavior
- [ ] Performance testing

### Step 7: Phase 2 Implementation (In Progress)
- [ ] Implement USA Spending server
- [x] Implement EPA Air Quality server
- [ ] Test all Phase 2 servers
- [x] Update documentation

### Step 8: Publishing & Deployment

- [ ] Create GitHub repository
- [ ] Set up CI/CD pipeline
- [ ] Publish to PyPI (optional)
- [ ] Create release notes
- [ ] Announce project

## API Key Requirements

| Service | API Key Required | How to Obtain |
|---------|------------------|---------------|
| Census Bureau | Yes (for higher rate limits) | https://api.census.gov/data/key_signup.html |
| SEC EDGAR | No | Public API |
| FDA openFDA | No | Public API |
| BLS | Yes | https://www.bls.gov/developers/api_signature_v2.htm |
| USA Spending | No | Public API |
| EPA AQS | Yes | https://aqs.epa.gov/data/api/signup |

## Configuration Examples

### Claude Desktop Configuration

```json
{
  "mcpServers": {
    "us-data-mcp.census-data": {
      "command": "uvx",
      "args": ["us-data-mcp.census-data@latest"],
      "env": {
        "CENSUS_API_KEY": "your-api-key-here"
      }
    },
    "us-data-mcp.sec-edgar": {
      "command": "uvx",
      "args": ["us-data-mcp.sec-edgar@latest"]
    },
    "us-data-mcp.fda-drugs": {
      "command": "uvx",
      "args": ["us-data-mcp.fda-drugs@latest"]
    },
    "us-data-mcp.bls-labor": {
      "command": "uvx",
      "args": ["us-data-mcp.bls-labor@latest"],
      "env": {
        "BLS_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Cline Configuration

```json
{
  "mcpServers": {
    "us-data-mcp.census-data": {
      "command": "python",
      "args": ["-m", "us_data_mcp.census_data.server"],
      "env": {
        "CENSUS_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## Success Metrics
- [x] All Phase 1 servers successfully deployed
- [ ] 100% test coverage for core functionality
- [x] Documentation complete and clear
- [x] Successfully tested with Claude Desktop
- [ ] Successfully tested with Cline
- [ ] Template system working for rapid server creation
- [ ] Phase 2 servers implemented (2/2)

## Future Enhancements

1. **Additional Data Sources**
   - NOAA Weather Data
   - NASA APIs
   - USGS Earthquake Data
   - National Park Service
   - IRS Tax Statistics

2. **Advanced Features**
   - Data caching layer
   - Rate limiting middleware
   - Response streaming for large datasets
   - Advanced query builders
   - Data transformation utilities

3. **Developer Tools**
   - CLI tool for testing servers
   - Mock server for development
   - API explorer web UI
   - Performance monitoring

## Timeline Estimate

- **Week 1**: Project setup, template development
- **Week 2**: Census Bureau and SEC EDGAR servers
- **Week 3**: FDA and BLS servers + documentation
- **Week 4**: Phase 2 servers, testing, polish
- **Total**: 4 weeks for complete Phase 1 & 2

## Resources & References

### US Government Data Portals
- Data.gov: https://data.gov/
- Census Bureau API: https://www.census.gov/data/developers/data-sets.html
- SEC EDGAR: https://www.sec.gov/edgar/sec-api-documentation
- FDA openFDA: https://open.fda.gov/apis/
- BLS API: https://www.bls.gov/developers/
- USA Spending: https://api.usaspending.gov/
- EPA AQS API: https://aqs.epa.gov/data/api

### MCP Resources
- MCP Specification: https://modelcontextprotocol.io/
- MCP Python SDK: https://github.com/modelcontextprotocol/python-sdk
- FastMCP: https://github.com/jlowin/fastmcp
- Claude MCP Documentation: https://docs.anthropic.com/claude/docs/model-context-protocol

### Inspiration
- Korean data.go.kr MCP servers: https://github.com/sechan9999/data-go-mcp-servers

## License

MIT License (to be consistent with the original project)

---

**Next Steps**: Begin with Step 1 - Project Setup
