# US Data.gov MCP Servers

US government public data portal (data.gov) API Model Context Protocol (MCP) servers.

## Table of Contents

- [What is MCP?](#what-is-mcp)
- [Why US Public Data MCP Servers?](#why-us-public-data-mcp-servers)
- [Available MCP Servers](#available-mcp-servers)
- [Installation & Setup](#installation--setup)
- [Usage for Each Server](#usage-for-each-server)
- [Developer Guide](#developer-guide)
- [Contributing](#contributing)
- [License](#license)

## What is MCP?

Model Context Protocol (MCP) is an open protocol that enables seamless integration between LLM applications and external data sources and tools. Whether you're building an AI-powered IDE, enhancing a chat interface, or creating custom AI workflows, MCP provides a standardized way to connect LLMs with the context they need.

MCP servers are lightweight programs that expose specific functionality through the Model Context Protocol. AI tools like Claude Desktop, Cline, Cursor, and Windsurf can communicate with these servers as MCP clients.

## Why US Public Data MCP Servers?

The US government's data.gov portal provides access to thousands of datasets from various federal agencies through APIs. This project wraps these APIs as MCP servers, enabling AI tools to easily access and utilize US public data.

### Key Benefits:

- **Standardized Access**: Use various public APIs through a unified MCP interface
- **AI Tool Integration**: Direct access to public data from Claude, Cline, and other AI assistants
- **Easy Installation**: Install via pip or uv
- **Type Safety**: Strong type validation using Pydantic
- **Developer Friendly**: Template-based rapid server creation

## Available MCP Servers

### Phase 1 - Core Servers

```
us-data-mcp.census-data
```
US Census Bureau demographic and economic data

```
us-data-mcp.sec-edgar
```
SEC EDGAR company filings and financial information

```
us-data-mcp.fda-drugs
```
FDA drug approvals, recalls, and safety information

```
us-data-mcp.bls-labor
```
Bureau of Labor Statistics employment and economic data

### Phase 2 - Extended Servers (Coming Soon)

```
us-data-mcp.usa-spending
```
Federal spending, contracts, and grants

```
us-data-mcp.epa-airquality
```
EPA air quality and environmental monitoring

## Installation & Setup

### Using UV (Recommended)

```bash
# Census data server
uv pip install us-data-mcp.census-data

# SEC EDGAR server
uv pip install us-data-mcp.sec-edgar

# FDA drugs server
uv pip install us-data-mcp.fda-drugs

# BLS labor statistics server
uv pip install us-data-mcp.bls-labor
```

### Using pip

```bash
# Census data server
pip install us-data-mcp.census-data

# SEC EDGAR server
pip install us-data-mcp.sec-edgar

# FDA drugs server
pip install us-data-mcp.fda-drugs

# BLS labor statistics server
pip install us-data-mcp.bls-labor
```

### Claude Desktop Configuration

Add MCP servers to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

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

**Note**: Using `@latest` ensures you always run the latest version.

### Cline Configuration

Configure MCP servers in VS Code's Cline extension:

`.vscode/cline_mcp_settings.json`:

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

## Usage for Each Server

### Census Bureau Data (us-data-mcp.census-data)

Access US Census Bureau demographic and economic data.

#### Environment Variables

```bash
export CENSUS_API_KEY="your-api-key-here"  # Get from https://api.census.gov/data/key_signup.html
```

#### Available Tools

`search_population`: Search population data by geography

**Parameters:**
- `year`: Year of data (e.g., 2020)
- `state`: State FIPS code (2 digits)
- `county`: County FIPS code (3 digits, optional)
- `variables`: List of census variables to retrieve

`search_economic`: Search economic indicators

**Parameters:**
- `year`: Year of data
- `dataset`: Dataset name (e.g., "acs/acs5")
- `variables`: List of economic variables
- `geography`: Geographic level (state, county, etc.)

#### Usage Examples

```
"Get population data for California in 2020"
"Find median household income for New York County"
"Show employment statistics for Texas"
```

### SEC EDGAR (us-data-mcp.sec-edgar)

Access SEC company filings and financial information.

#### Environment Variables

No API key required - uses public SEC EDGAR API.

#### Available Tools

`search_company`: Search for company information

**Parameters:**
- `company_name`: Company name or ticker symbol
- `cik`: Central Index Key (optional)

`get_filings`: Get company filings

**Parameters:**
- `cik`: Central Index Key
- `form_type`: Filing type (10-K, 10-Q, 8-K, etc.)
- `count`: Number of recent filings to retrieve (default: 10)

`get_filing_content`: Get specific filing content

**Parameters:**
- `accession_number`: Filing accession number
- `cik`: Central Index Key

#### Usage Examples

```
"Find recent 10-K filings for Apple"
"Get the latest 8-K filing for Tesla"
"Search for company with ticker MSFT"
```

### FDA Drug Information (us-data-mcp.fda-drugs)

Access FDA drug approvals, recalls, and safety information.

#### Environment Variables

No API key required - uses public openFDA API.

#### Available Tools

`search_drugs`: Search drug database

**Parameters:**
- `brand_name`: Brand name of drug (optional)
- `generic_name`: Generic name (optional)
- `application_number`: FDA application number (optional)
- `limit`: Max results (default: 10)

`search_recalls`: Search drug recalls

**Parameters:**
- `product_description`: Product description
- `classification`: Recall classification (I, II, III)
- `status`: Recall status (ongoing, completed)
- `limit`: Max results (default: 10)

`search_adverse_events`: Search adverse event reports

**Parameters:**
- `drug_name`: Drug name
- `reaction`: Specific reaction/side effect (optional)
- `limit`: Max results (default: 10)

#### Usage Examples

```
"Find FDA approval info for Lipitor"
"Search for recent drug recalls"
"Get adverse event reports for aspirin"
```

### BLS Labor Statistics (us-data-mcp.bls-labor)

Access Bureau of Labor Statistics employment and economic data.

#### Environment Variables

```bash
export BLS_API_KEY="your-api-key-here"  # Get from https://www.bls.gov/developers/api_signature_v2.htm
```

#### Available Tools

`get_employment_data`: Get employment statistics

**Parameters:**
- `series_id`: BLS series ID
- `start_year`: Start year
- `end_year`: End year

`search_cpi`: Get Consumer Price Index data

**Parameters:**
- `area`: Geographic area code
- `item`: CPI item code
- `start_year`: Start year
- `end_year`: End year

`get_unemployment_rate`: Get unemployment rate

**Parameters:**
- `state`: State name or code
- `start_year`: Start year
- `end_year`: End year

#### Usage Examples

```
"Get unemployment rate for California from 2020 to 2023"
"Find CPI data for urban areas"
"Show employment statistics for the tech sector"
```

## Developer Guide

### Development Environment Setup

```bash
# Clone repository
git clone https://github.com/sechan9999/us-data-mcp-servers.git
cd us-data-mcp-servers

# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync --dev
```

### 🚀 Quickly Create a New MCP Server

#### Using Automation Script (Recommended)

The fastest way is to use the provided template generation script:

```bash
# Run interactive script
uv run python scripts/create_mcp_server.py
```

The script will guide you through the process step-by-step and generate a new MCP server in minutes.

#### Manual Template Usage

```bash
# Install Cookiecutter (if needed)
uv pip install cookiecutter

# Create new server from template
uv run cookiecutter template/ -o src/
```

For detailed template usage, see [TEMPLATE_USAGE.md](TEMPLATE_USAGE.md).

For the complete developer guide, see [CONTRIBUTING.md](CONTRIBUTING.md).

### Running Tests

```bash
# Run all tests
uv run pytest

# Run tests for specific server
uv run pytest src/census-data/tests/
```

## API Keys

| Service | API Key Required | Sign Up Link |
|---------|------------------|--------------|
| Census Bureau | Recommended (higher rate limits) | https://api.census.gov/data/key_signup.html |
| SEC EDGAR | No | N/A |
| FDA openFDA | No | N/A |
| BLS | Yes | https://www.bls.gov/developers/api_signature_v2.htm |

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

Inspired by the [Korean data.go.kr MCP servers](https://github.com/sechan9999/data-go-mcp-servers) project.

## Resources

- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [Data.gov Developer Resources](https://data.gov/developers/)
- [Census API Documentation](https://www.census.gov/data/developers/guidance.html)
- [SEC EDGAR API](https://www.sec.gov/edgar/sec-api-documentation)
- [openFDA API](https://open.fda.gov/apis/)
- [BLS API Documentation](https://www.bls.gov/developers/)
