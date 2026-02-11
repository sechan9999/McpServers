# US Data MCP Servers - Architecture Diagram

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        AI Clients                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Claude     │  │    Cline     │  │   Cursor     │          │
│  │   Desktop    │  │   (VS Code)  │  │  Windsurf    │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          └──────────────────┴──────────────────┘
                             │
                    Model Context Protocol (MCP)
                             │
          ┌──────────────────┴──────────────────┐
          │                                     │
┌─────────▼──────────┐              ┌──────────▼──────────┐
│  Census MCP Server │              │  Future MCP Servers │
│  (Implemented ✅)  │              │  (Planned 🔄)       │
├────────────────────┤              ├─────────────────────┤
│ Tools:             │              │ • SEC EDGAR         │
│ • search_pop       │              │ • FDA Drugs         │
│ • search_econ      │              │ • BLS Labor         │
│ • get_variables    │              │ • USA Spending      │
│ • get_fips         │              │ • EPA Air Quality   │
└─────────┬──────────┘              └─────────────────────┘
          │
          │ HTTP/REST API
          │
┌─────────▼──────────────────────────────────────────────┐
│         US Government Public Data APIs                 │
│  ┌──────────────────────────────────────────────┐     │
│  │   Census Bureau API                          │     │
│  │   https://api.census.gov/data                │     │
│  └──────────────────────────────────────────────┘     │
│                                                        │
│  Other APIs (for future servers):                     │
│  • SEC EDGAR: https://www.sec.gov/edgar               │
│  • FDA openFDA: https://api.fda.gov                   │
│  • BLS: https://api.bls.gov/publicAPI/v2              │
│  • USA Spending: https://api.usaspending.gov          │
│  • EPA AQS: https://aqs.epa.gov/data/api              │
└────────────────────────────────────────────────────────┘
```

## MCP Server Internal Architecture

Each MCP server follows this modular architecture:

```
┌───────────────────────────────────────────────────────────┐
│                    MCP Server                             │
│                                                           │
│  ┌─────────────────────────────────────────────────┐    │
│  │              server.py                          │    │
│  │  ┌────────────────────────────────────────┐    │    │
│  │  │  MCP Protocol Handler                  │    │    │
│  │  │  • list_tools()                        │    │    │
│  │  │  • call_tool()                         │    │    │
│  │  │  • Tool definitions & schemas          │    │    │
│  │  └────────────┬───────────────────────────┘    │    │
│  └───────────────┼────────────────────────────────┘    │
│                  │                                       │
│  ┌───────────────▼────────────────────────────────┐    │
│  │              models.py                         │    │
│  │  ┌──────────────────────────────────────┐     │    │
│  │  │  Pydantic Models (Type Safety)       │     │    │
│  │  │  • Request schemas                   │     │    │
│  │  │  • Response schemas                  │     │    │
│  │  │  • Data validation                   │     │    │
│  │  │  • Common constants                  │     │    │
│  │  └──────────────┬───────────────────────┘     │    │
│  └─────────────────┼─────────────────────────────┘    │
│                    │                                    │
│  ┌─────────────────▼─────────────────────────────┐    │
│  │           api_client.py                       │    │
│  │  ┌────────────────────────────────────────┐  │    │
│  │  │  API Interaction Layer                 │  │    │
│  │  │  • Async HTTP client (httpx)           │  │    │
│  │  │  • URL building                        │  │    │
│  │  │  • Request formatting                  │  │    │
│  │  │  • Response parsing                    │  │    │
│  │  │  • Error handling                      │  │    │
│  │  │  • Rate limiting                       │  │    │
│  │  │  • API key management                  │  │    │
│  │  └────────────────┬───────────────────────┘  │    │
│  └───────────────────┼──────────────────────────┘    │
└────────────────────────┼─────────────────────────────┘
                         │
                         │ HTTPS
                         ▼
              [ Government API ]
```

## Data Flow Example

### Example: "Get 2020 population for California"

```
1. User Query (in Claude Desktop)
   │
   │  "Get 2020 population data for California"
   │
   ▼
2. Claude interprets and calls MCP tool
   │
   │  Tool: search_population
   │  Params: {year: 2020, state: "06"}
   │
   ▼
3. MCP Server (server.py)
   │
   │  • Validates parameters using Pydantic
   │  • Calls api_client.get_population_data()
   │
   ▼
4. API Client (api_client.py)
   │
   │  • Builds URL: https://api.census.gov/data/2020/acs/acs5
   │  • Adds params: get=NAME,B01001_001E&for=state:06&key=...
   │  • Makes async HTTP request
   │
   ▼
5. Census Bureau API
   │
   │  • Processes request
   │  • Returns JSON data
   │
   ▼
6. API Client processes response
   │
   │  • Parses JSON
   │  • Formats as CensusResponse model
   │  • Adds metadata (variable descriptions)
   │
   ▼
7. MCP Server returns to Claude
   │
   │  {
   │    "data": [
   │      {
   │        "NAME": "California",
   │        "B01001_001E": "39538223",
   │        "state": "06"
   │      }
   │    ],
   │    "metadata": {
   │      "year": 2020,
   │      "variables": {
   │        "B01001_001E": "Total Population"
   │      }
   │    }
   │  }
   │
   ▼
8. Claude formats response for user
   │
   │  "California had a population of 39,538,223 in 2020."
   │
   ▼
9. User sees natural language response
```

## Component Responsibilities

### server.py
- **MCP Protocol**: Implements MCP server specification
- **Tool Definitions**: Declares available tools and their schemas
- **Request Routing**: Routes tool calls to appropriate handlers
- **Response Formatting**: Formats data for MCP clients
- **Lifecycle**: Manages server initialization and cleanup

### models.py
- **Type Safety**: Pydantic models for all data structures
- **Validation**: Automatic validation of inputs/outputs
- **Documentation**: Self-documenting schemas
- **Constants**: Common variable definitions and references
- **Serialization**: JSON serialization/deserialization

### api_client.py
- **HTTP Communication**: Async requests to government APIs
- **Authentication**: API key management
- **Rate Limiting**: Respects API rate limits
- **Error Handling**: Comprehensive error handling and retries
- **Data Transformation**: Converts API responses to internal models
- **Caching**: (Future) Response caching for performance

## Technology Stack

```
┌─────────────────────────────────────────────┐
│           Application Layer                 │
│                                             │
│  ┌─────────────────────────────────────┐  │
│  │  MCP SDK (mcp package)              │  │
│  │  • Server implementation            │  │
│  │  • Protocol handlers                │  │
│  │  • Stdio transport                  │  │
│  └─────────────────────────────────────┘  │
│                                             │
│  ┌─────────────────────────────────────┐  │
│  │  Pydantic                           │  │
│  │  • Data validation                  │  │
│  │  • Type safety                      │  │
│  │  • JSON schema generation           │  │
│  └─────────────────────────────────────┘  │
│                                             │
│  ┌─────────────────────────────────────┐  │
│  │  httpx                              │  │
│  │  • Async HTTP client                │  │
│  │  • Connection pooling               │  │
│  │  • Retry logic                      │  │
│  └─────────────────────────────────────┘  │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│         Development & Testing               │
│                                             │
│  pytest • pytest-asyncio • pytest-cov      │
│  black • ruff • mypy                       │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│        Package Management                   │
│                                             │
│  UV - Fast Python package installer        │
└─────────────────────────────────────────────┘
```

## Deployment Patterns

### Pattern 1: Direct Execution (Development)
```
Claude Desktop → Python Process → MCP Server → API
```

### Pattern 2: Published Package (Production)
```
Claude Desktop → uvx → PyPI Package → MCP Server → API
```

### Pattern 3: Cline Integration (VS Code)
```
Cline Extension → Python Module → MCP Server → API
```

## Security & Best Practices

### API Key Management
```
Environment Variables (✅ Recommended)
  ↓
.env files (Development)
  ↓
System environment (Production)
  ↓
Never in code or version control
```

### Error Handling Flow
```
Try: API Request
  ↓
Catch: HTTP Errors → Return error in response
  ↓
Catch: Validation Errors → Return validation message
  ↓
Catch: Network Errors → Return network error
  ↓
Always: Log for debugging
  ↓
Always: Return structured response
```

### Type Safety Chain
```
User Input
  ↓
JSON Schema Validation (MCP)
  ↓
Pydantic Model Validation
  ↓
Type-checked processing
  ↓
Validated response
  ↓
JSON serialization
```

## Scaling Considerations

### Current Implementation (Phase 1)
- Single server per data source
- Direct API calls (no caching)
- Environment-based configuration
- Synchronous Claude interaction

### Future Enhancements
- Response caching layer (Redis/SQLite)
- Rate limiting middleware
- Connection pooling
- Batch request support
- Multi-source aggregation
- Persistent storage for historical data

## File Organization

```
us_data_mcp_servers/
│
├── Root Documentation
│   ├── README.md              # Project overview
│   ├── QUICKSTART.md          # Getting started
│   ├── IMPLEMENTATION_PLAN.md # Development roadmap
│   └── PROJECT_SUMMARY.md     # Current status
│
├── Configuration
│   ├── pyproject.toml         # Project metadata
│   ├── .env.example           # API key template
│   └── .gitignore             # Version control
│
├── examples/
│   └── census_example.py      # Direct usage examples
│
└── src/
    └── [server-name]/         # Each MCP server
        ├── README.md          # Server-specific docs
        ├── pyproject.toml     # Server metadata
        ├── src/
        │   └── us_data_mcp/
        │       └── [server_name]/
        │           ├── server.py      # MCP implementation
        │           ├── models.py      # Data models
        │           └── api_client.py  # API interaction
        └── tests/
            └── test_*.py      # Unit tests
```

This modular structure allows:
- **Independent deployment**: Each server can be published separately
- **Isolated dependencies**: Servers don't interfere with each other
- **Clear separation**: Easy to understand and maintain
- **Scalability**: Add new servers without affecting existing ones
