# Quick Start Guide

## Get Started in 5 Minutes

### 1. Get API Keys

**Census Bureau** (Recommended for higher rate limits):
1. Visit https://api.census.gov/data/key_signup.html
2. Fill out the form with your name and organization
3. Check your email for the API key

**Bureau of Labor Statistics** (Required for BLS server):
1. Visit https://www.bls.gov/developers/api_signature_v2.htm
2. Fill out the registration form
3. Receive your API key via email

### 2. Set Up Environment

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env

# Edit it with your API keys
# CENSUS_API_KEY=your_actual_key_here
# BLS_API_KEY=your_actual_key_here
```

### 3. Install UV (if not already installed)

**Linux/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 4. Install Dependencies

```bash
# Install development dependencies
uv sync --dev
```

### 5. Test the Census Server

```bash
# Set your API key
export CENSUS_API_KEY="your-key-here"  # Linux/macOS
$env:CENSUS_API_KEY="your-key-here"    # Windows PowerShell

# Run tests
uv run pytest src/census-data/tests/ -v

# Or test manually
uv run python -m us_data_mcp.census_data.server
```

### 6. Configure Claude Desktop

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

Add the Census server:

```json
{
  "mcpServers": {
    "census-data": {
      "command": "uvx",
      "args": ["us-data-mcp.census-data@latest"],
      "env": {
        "CENSUS_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

**Note for local development**: If you haven't published to PyPI yet, use:

```json
{
  "mcpServers": {
    "census-data": {
      "command": "python",
      "args": ["-m", "us_data_mcp.census_data.server"],
      "env": {
        "CENSUS_API_KEY": "your-api-key-here"
      },
      "cwd": "C:/Users/secha/.gemini/antigravity/scratch/mcp_agents/us_data_mcp_servers/src/census-data/src"
    }
  }
}
```

### 7. Restart Claude Desktop

After updating the config file, restart Claude Desktop to load the MCP server.

### 8. Try It Out!

In Claude Desktop, try these queries:

```
"What's the FIPS code for California?"

"Get population data for California in 2020"

"Show me common Census variables for economic data"

"Find median household income for New York state in 2021"
```

## Quick Reference

### State FIPS Codes (Top 10 by Population)

| State | FIPS |
|-------|------|
| California | 06 |
| Texas | 48 |
| Florida | 12 |
| New York | 36 |
| Pennsylvania | 42 |
| Illinois | 17 |
| Ohio | 39 |
| Georgia | 13 |
| North Carolina | 37 |
| Michigan | 26 |

### Common Variables

**Population:**
- `B01001_001E` - Total Population
- `B01002_001E` - Median Age

**Economic:**
- `B19013_001E` - Median Household Income
- `B17001_002E` - Below Poverty Level
- `B23025_005E` - Unemployed

**Housing:**
- `B25077_001E` - Median Home Value
- `B25001_001E` - Total Housing Units

## Next Steps

1. **Explore More Data**: Use `get_common_variables` to discover more variables
2. **Add More Servers**: Follow the implementation plan for SEC, FDA, and BLS servers
3. **Customize**: Modify the servers to fit your specific use cases
4. **Contribute**: See CONTRIBUTING.md for how to add new servers

## Troubleshooting

### "Census API key is required" Error

Make sure:
1. You've set the `CENSUS_API_KEY` environment variable
2. The API key is valid (check your email)
3. The environment variable is accessible to the process

### Empty Data Results

1. Verify FIPS codes are correct (use `get_state_fips`)
2. Check that the year has available data for that dataset
3. Ensure variable codes are valid (use `get_common_variables`)

### Server Not Showing in Claude

1. Check that the config file path is correct
2. Verify JSON syntax is valid (use a JSON validator)
3. Restart Claude Desktop after config changes
4. Check Claude Desktop logs for errors

## Resources

- [Census API Documentation](https://www.census.gov/data/developers/guidance.html)
- [MCP Protocol Docs](https://modelcontextprotocol.io/)
- [Project README](README.md)
- [Implementation Plan](IMPLEMENTATION_PLAN.md)
