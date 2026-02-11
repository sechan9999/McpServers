"""Tests for Census API client."""

import pytest
from unittest.mock import AsyncMock, patch
from us_data_mcp.census_data.api_client import CensusAPIClient
from us_data_mcp.census_data.models import CensusResponse


@pytest.fixture
def api_key():
    """Fixture for API key."""
    return "test_api_key_12345"


@pytest.fixture
async def census_client(api_key):
    """Fixture for Census API client."""
    client = CensusAPIClient(api_key=api_key)
    yield client
    await client.close()


class TestCensusAPIClient:
    """Test cases for CensusAPIClient."""
    
    def test_init_with_api_key(self, api_key):
        """Test initialization with API key."""
        client = CensusAPIClient(api_key=api_key)
        assert client.api_key == api_key
    
    def test_init_without_api_key(self):
        """Test initialization without API key raises error."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="Census API key is required"):
                CensusAPIClient()
    
    def test_build_url(self, census_client):
        """Test URL building."""
        url = census_client._build_url(2020, "acs/acs5")
        assert url == "https://api.census.gov/data/2020/acs/acs5"
    
    def test_build_params_state_only(self, census_client):
        """Test parameter building for state-level query."""
        params = census_client._build_params(
            variables=["NAME", "B01001_001E"],
            geography="state:06",
            state="06"
        )
        
        assert params["get"] == "NAME,B01001_001E"
        assert params["for"] == "state:06"
        assert "key" in params
    
    def test_build_params_county(self, census_client):
        """Test parameter building for county-level query."""
        params = census_client._build_params(
            variables=["NAME", "B01001_001E"],
            geography="county:*",
            state="06",
            county="001"
        )
        
        assert params["get"] == "NAME,B01001_001E"
        assert params["for"] == "county:001"
        assert params["in"] == "state:06"
    
    @pytest.mark.asyncio
    async def test_get_data_success(self, census_client):
        """Test successful data retrieval."""
        # Mock response data
        mock_response_data = [
            ["NAME", "B01001_001E", "state"],
            ["California", "39538223", "06"]
        ]
        
        with patch.object(census_client.client, "get") as mock_get:
            mock_response = AsyncMock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status = AsyncMock()
            mock_get.return_value = mock_response
            
            result = await census_client.get_data(
                year=2020,
                dataset="acs/acs5",
                variables=["NAME", "B01001_001E"],
                geography="state:*"
            )
            
            assert result.success is True
            assert len(result.data) == 1
            assert result.data[0]["NAME"] == "California"
            assert result.data[0]["B01001_001E"] == "39538223"
    
    @pytest.mark.asyncio
    async def test_get_population_data(self, census_client):
        """Test population data retrieval."""
        mock_response_data = [
            ["NAME", "B01001_001E", "B01002_001E", "state"],
            ["California", "39538223", "36.5", "06"]
        ]
        
        with patch.object(census_client.client, "get") as mock_get:
            mock_response = AsyncMock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status = AsyncMock()
            mock_get.return_value = mock_response
            
            result = await census_client.get_population_data(
                year=2020,
                state="06"
            )
            
            assert result.success is True
            assert len(result.data) == 1
            assert "NAME" in result.data[0]
    
    @pytest.mark.asyncio
    async def test_get_economic_data(self, census_client):
        """Test economic data retrieval."""
        mock_response_data = [
            ["NAME", "B19013_001E", "state"],
            ["California", "75235", "06"]
        ]
        
        with patch.object(census_client.client, "get") as mock_get:
            mock_response = AsyncMock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status = AsyncMock()
            mock_get.return_value = mock_response
            
            result = await census_client.get_economic_data(
                year=2020,
                state="06"
            )
            
            assert result.success is True
            assert len(result.data) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
