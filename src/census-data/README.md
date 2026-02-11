# US Census Bureau Data MCP Server

Access US Census Bureau demographic and economic data through the Model Context Protocol.

## Features

- 🏘️ **Population Data**: Access population statistics, median age, and demographic information
- 💰 **Economic Data**: Retrieve income, poverty, and unemployment statistics  
- 🗺️ **Geographic Flexibility**: Query data at state and county levels
- 📊 **Multiple Variables**: Access hundreds of census variables through a unified interface
- 🔍 **Reference Tools**: Built-in helpers for FIPS codes and variable descriptions

## Installation

### Using UV (Recommended)

```bash
uv pip install us-data-mcp.census-data
```

### Using pip

```bash
pip install us-data-mcp.census-data
```

## Configuration

### Get a Census API Key

1. Visit https://api.census.gov/data/key_signup.html
2. Fill out the registration form
3. Check your email for the API key

### Set Environment Variable

```bash
# Linux/macOS
export CENSUS_API_KEY="your-api-key-here"

# Windows PowerShell
$env:CENSUS_API_KEY="your-api-key-here"
```

### Claude Desktop Setup

Add to your `claude_desktop_config.json`:

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

### Cline Setup

Add to `.vscode/cline_mcp_settings.json`:

```json
{
  "mcpServers": {
    "census-data": {
      "command": "python",
      "args": ["-m", "us_data_mcp.census_data.server"],
      "env": {
        "CENSUS_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## Available Tools

### search_population

Search population data by geographic area.

**Parameters:**
- `year` (required): Year of census data (2000-2030)
- `state` (required): State FIPS code (2 digits, e.g., "06" for California)
- `county` (optional): County FIPS code (3 digits)
- `variables` (optional): List of census variable codes

**Default Variables:**
- `NAME`: Geographic area name
- `B01001_001E`: Total population
- `B01002_001E`: Median age

**Example:**
```
"Get population data for California in 2020"
"Find population and median age for Los Angeles County (state: 06, county: 037)"
```

### search_economic

Search economic indicator data.

**Parameters:**
- `year` (required): Year of data
- `dataset` (optional): Dataset name (default: "acs/acs5")
- `variables` (optional): List of economic variable codes
- `geography` (optional): Geographic level (default: "state:*")
- `state` (optional): State FIPS code filter

**Default Variables:**
- `NAME`: Geographic area name
- `B19013_001E`: Median household income
- `B17001_002E`: Population below poverty level
- `B23025_005E`: Unemployment

**Example:**
```
"Get median household income for all states in 2021"
"Find poverty and unemployment data for New York (state: 36)"
```

### get_common_variables

Get a reference list of commonly used Census variables organized by category.

**Categories:**
- Population
- Economic
- Housing
- Education
- Demographics

**Example:**
```
"Show me common Census variables"
"What variables are available for education data?"
```

### get_state_fips

Get FIPS codes for US states.

**Parameters:**
- `state_name` (optional): State name to look up

**Example:**
```
"What is the FIPS code for California?"
"Show all state FIPS codes"
```

## Common Census Variables

### Population
- `B01001_001E`: Total Population
- `B01002_001E`: Median Age
- `B01003_001E`: Total Population (alternative)

### Economic
- `B19013_001E`: Median Household Income
- `B19301_001E`: Per Capita Income
- `B17001_002E`: Population Below Poverty Level
- `B23025_005E`: Unemployed Population

### Housing
- `B25001_001E`: Total Housing Units
- `B25002_002E`: Occupied Housing Units
- `B25002_003E`: Vacant Housing Units
- `B25077_001E`: Median Home Value

### Education
- `B15003_022E`: Population with Bachelor's Degree
- `B15003_023E`: Population with Master's Degree
- `B15003_024E`: Population with Professional Degree
- `B15003_025E`: Population with Doctorate Degree

### Race & Ethnicity
- `B02001_002E`: White Alone
- `B02001_003E`: Black or African American Alone
- `B02001_004E`: American Indian and Alaska Native Alone
- `B02001_005E`: Asian Alone
- `B03001_003E`: Hispanic or Latino

## State FIPS Codes (Common)

| State | FIPS Code |
|-------|-----------|
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

Use the `get_state_fips` tool to get the complete list.

## Usage Examples

### Example 1: Population Data for California

**Query:** "Get 2020 population data for California"

**Response:**
```json
{
  "data": [
    {
      "NAME": "California",
      "B01001_001E": "39538223",
      "B01002_001E": "36.5",
      "state": "06"
    }
  ],
  "metadata": {
    "year": 2020,
    "dataset": "acs/acs5",
    "variables": {
      "B01001_001E": "Total Population",
      "B01002_001E": "Median Age"
    },
    "count": 1
  },
  "success": true
}
```

### Example 2: Economic Data for Multiple States

**Query:** "Get median household income for California, Texas, and New York in 2021"

**Response:**
```json
{
  "data": [
    {
      "NAME": "California",
      "B19013_001E": "78672",
      "state": "06"
    },
    {
      "NAME": "Texas",
      "B19013_001E": "63826",
      "state": "48"
    },
    {
      "NAME": "New York",
      "B19013_001E": "72108",
      "state": "36"
    }
  ],
  "metadata": {
    "year": 2021,
    "dataset": "acs/acs5",
    "variables": {
      "B19013_001E": "Median Household Income"
    },
    "count": 3
  },
  "success": true
}
```

## Development

### Run Tests

```bash
pytest
```

### Run Specific Tests

```bash
pytest tests/test_api_client.py -v
```

## Troubleshooting

### API Key Error

If you see `"Census API key is required"`:
1. Ensure you've set the `CENSUS_API_KEY` environment variable
2. Verify the API key is valid
3. Check that it's properly configured in your MCP client settings

### Rate Limiting

The Census API has rate limits:
- Without API key: 500 requests per day
- With API key: Much higher limits (typically sufficient for most use cases)

If you hit rate limits, wait before retrying or upgrade your API key.

### Data Not Found

If a query returns empty data:
1. Verify the year is within the available range for the dataset
2. Check that FIPS codes are correct (use `get_state_fips` tool)
3. Ensure variable codes are valid (use `get_common_variables` tool)
4. Some datasets may not have data for all years/geographies

## Resources

- [Census API Documentation](https://www.census.gov/data/developers/guidance.html)
- [Available Datasets](https://www.census.gov/data/developers/data-sets.html)
- [Variable Explorer](https://api.census.gov/data.html)
- [Geography Reference](https://www.census.gov/programs-surveys/geography/guidance/geo-identifiers.html)

## License

MIT License
