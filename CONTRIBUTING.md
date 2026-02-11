# Contributing to US Data MCP Servers

Thank you for your interest in contributing! This guide will help you add new MCP servers for US government data sources.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Adding a New MCP Server](#adding-a-new-mcp-server)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)

## Getting Started

### Prerequisites

- Python 3.11 or higher
- UV package manager
- Git
- A US government API key (if required by your data source)

### Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/us-data-mcp-servers.git
cd us-data-mcp-servers

# Add upstream remote
git remote add upstream https://github.com/sechan9999/us-data-mcp-servers.git
```

## Development Setup

### 1. Install UV

**Linux/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Install Dependencies

```bash
uv sync --dev
```

### 3. Set Up Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API keys
```

## Adding a New MCP Server

### Step 1: Choose Your Data Source

Select a US government API from:
- [Data.gov catalog](https://catalog.data.gov/dataset)
- [API.data.gov](https://api.data.gov/)
- Federal agency websites (CDC, NOAA, NASA, etc.)

Requirements:
- Must be a public US government data source
- Should have a documented API
- Should provide useful data for AI applications

### Step 2: Create Server Structure

Follow the Census server structure:

```
src/
└── [your-server-name]/
    ├── README.md
    ├── pyproject.toml
    ├── src/
    │   └── us_data_mcp/
    │       └── [your_server_name]/
    │           ├── __init__.py
    │           ├── server.py      # MCP server implementation
    │           ├── models.py      # Pydantic models
    │           └── api_client.py  # API interaction
    └── tests/
        ├── __init__.py
        └── test_api_client.py
```

### Step 3: Implement Components

#### 3.1 Create models.py

Define Pydantic models for requests and responses:

```python
from typing import Optional, List
from pydantic import BaseModel, Field

class YourDataRequest(BaseModel):
    """Request model for your data."""
    
    param1: str = Field(..., description="Description of param1")
    param2: Optional[int] = Field(None, description="Optional param2")

class YourDataResponse(BaseModel):
    """Response model for your data."""
    
    data: List[dict] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
    success: bool = Field(default=True)
    error: Optional[str] = Field(None)
```

#### 3.2 Create api_client.py

Implement the API client:

```python
import os
from typing import Optional
import httpx
from dotenv import load_dotenv

from .models import YourDataResponse

load_dotenv()

class YourAPIClient:
    """Client for your government API."""
    
    BASE_URL = "https://api.example.gov"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("YOUR_API_KEY")
        # Only raise error if API key is actually required
        if self.requires_api_key() and not self.api_key:
            raise ValueError(
                "API key is required. Set YOUR_API_KEY environment variable."
            )
        
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={"User-Agent": "US-Data-MCP-Your-Server/0.1.0"}
        )
    
    @staticmethod
    def requires_api_key() -> bool:
        """Return whether this API requires a key."""
        return True  # Change to False if no key needed
    
    async def close(self) -> None:
        await self.client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def get_data(self, param1: str, param2: Optional[int] = None) -> YourDataResponse:
        """Fetch data from the API."""
        try:
            params = {"param1": param1}
            if param2:
                params["param2"] = param2
            if self.api_key:
                params["api_key"] = self.api_key
            
            response = await self.client.get(
                f"{self.BASE_URL}/endpoint",
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            
            return YourDataResponse(
                data=data,
                metadata={"source": "your-api"},
                success=True
            )
        
        except Exception as e:
            return YourDataResponse(
                data=[],
                metadata={},
                success=False,
                error=str(e)
            )
```

#### 3.3 Create server.py

Implement the MCP server:

```python
import asyncio
import json
from typing import Any, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .api_client import YourAPIClient
from .models import YourDataRequest

app = Server("us-data-mcp.your-server")
api_client: Optional[YourAPIClient] = None

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="your_tool_name",
            description="Description of what your tool does",
            inputSchema={
                "type": "object",
                "properties": {
                    "param1": {
                        "type": "string",
                        "description": "Description of param1"
                    }
                },
                "required": ["param1"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    global api_client
    
    try:
        if name == "your_tool_name":
            # Validate request
            request = YourDataRequest(**arguments)
            
            # Initialize client if needed
            if api_client is None:
                api_client = YourAPIClient()
            
            # Get data
            response = await api_client.get_data(
                param1=request.param1,
                param2=request.param2
            )
            
            return [TextContent(
                type="text",
                text=json.dumps(response.model_dump(), indent=2)
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
                "error": str(e)
            }, indent=2)
        )]

async def main():
    """Main entry point."""
    global api_client
    
    try:
        if YourAPIClient.requires_api_key():
            api_client = YourAPIClient()
        
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    finally:
        if api_client:
            await api_client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### Step 4: Create Tests

Write comprehensive tests in `tests/test_api_client.py`:

```python
import pytest
from unittest.mock import AsyncMock, patch
from us_data_mcp.your_server.api_client import YourAPIClient

@pytest.fixture
async def api_client():
    """Fixture for API client."""
    if YourAPIClient.requires_api_key():
        client = YourAPIClient(api_key="test_key")
    else:
        client = YourAPIClient()
    yield client
    await client.close()

@pytest.mark.asyncio
async def test_get_data_success(api_client):
    """Test successful data retrieval."""
    mock_response_data = {"result": "success"}
    
    with patch.object(api_client.client, "get") as mock_get:
        mock_response = AsyncMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = AsyncMock()
        mock_get.return_value = mock_response
        
        result = await api_client.get_data(param1="test")
        
        assert result.success is True
        assert len(result.data) > 0
```

### Step 5: Create Documentation

Create `README.md` for your server:

```markdown
# [Your Data Source] MCP Server

Brief description of what data this server provides.

## Features

- Feature 1
- Feature 2

## Installation

\`\`\`bash
uv pip install us-data-mcp.your-server
\`\`\`

## Configuration

### Environment Variables

\`\`\`bash
export YOUR_API_KEY="your-key-here"
\`\`\`

## Available Tools

### tool_name

Description of the tool.

**Parameters:**
- `param1`: Description

**Example:**
\`\`\`
"Example query in natural language"
\`\`\`

## Usage Examples

[Provide real-world examples]
```

### Step 6: Create pyproject.toml

```toml
[project]
name = "us-data-mcp.your-server"
version = "0.1.0"
description = "Your server description"
requires-python = ">=3.11"

dependencies = [
    "mcp>=0.1.0",
    "pydantic>=2.0.0",
    "httpx>=0.27.0",
    "python-dotenv>=1.0.0",
]

[project.scripts]
your-server = "us_data_mcp.your_server.server:main"
```

## Code Standards

### Style Guidelines

- **Formatting**: Use `black` for code formatting
- **Linting**: Use `ruff` for linting
- **Type Hints**: Use type hints everywhere
- **Docstrings**: Google-style docstrings for all functions/classes

### Run Code Quality Checks

```bash
# Format code
uv run black src/your-server/

# Lint code
uv run ruff check src/your-server/

# Type check
uv run mypy src/your-server/
```

### Code Patterns to Follow

1. **Use async/await**: All API calls should be async
2. **Error handling**: Always return structured responses
3. **Type safety**: Use Pydantic models for validation
4. **Environment variables**: Use `python-dotenv` for configuration
5. **Logging**: Use structured logging (future enhancement)

### What to Avoid

- ❌ Hardcoded API keys or secrets
- ❌ Blocking I/O operations
- ❌ Unhandled exceptions
- ❌ Missing type hints
- ❌ Untested code

## Testing

### Run All Tests

```bash
uv run pytest
```

### Run Specific Server Tests

```bash
uv run pytest src/your-server/tests/ -v
```

### Test Coverage

```bash
uv run pytest --cov=src/your-server --cov-report=html
```

### Testing Checklist

- [ ] Unit tests for API client
- [ ] Tests for all tool functions
- [ ] Error handling tests
- [ ] Mock external API calls
- [ ] Test with and without API key (if applicable)
- [ ] Test edge cases and validation

## Documentation

### Required Documentation

1. **Server README**: Usage guide with examples
2. **Docstrings**: All public functions and classes
3. **Type hints**: All function signatures
4. **Examples**: Real-world usage examples
5. **API reference**: Link to official API docs

### Documentation Checklist

- [ ] Installation instructions
- [ ] API key setup (if needed)
- [ ] Tool descriptions with parameters
- [ ] Usage examples with expected output
- [ ] Troubleshooting section
- [ ] Link to official data source documentation

## Submitting Changes

### 1. Create a Branch

```bash
git checkout -b feature/add-your-server
```

### 2. Make Your Changes

Follow the guides above to implement your server.

### 3. Test Thoroughly

```bash
# Run tests
uv run pytest src/your-server/tests/ -v

# Run code quality checks
uv run black src/your-server/
uv run ruff check src/your-server/
uv run mypy src/your-server/
```

### 4. Commit Your Changes

```bash
git add .
git commit -m "feat: Add [Your Data Source] MCP server

- Implement API client for [data source]
- Add [number] tools for [functionality]
- Include comprehensive tests and documentation
"
```

### 5. Push and Create Pull Request

```bash
git push origin feature/add-your-server
```

Then create a pull request on GitHub with:
- Clear description of what the server does
- List of tools implemented
- Example queries that work
- Screenshots/examples if helpful

### Pull Request Checklist

- [ ] Server follows project structure
- [ ] All tests pass
- [ ] Code passes quality checks (black, ruff, mypy)
- [ ] Documentation is complete
- [ ] Examples are provided
- [ ] pyproject.toml is configured correctly
- [ ] No hardcoded secrets or API keys

## Getting Help

- **Questions**: Open a GitHub discussion
- **Issues**: Create a GitHub issue
- **Examples**: Check the Census server implementation
- **Architecture**: See ARCHITECTURE.md

## Recognition

Contributors will be recognized in:
- Project README
- Release notes
- Contributors list

Thank you for contributing to US Data MCP Servers! 🎉
