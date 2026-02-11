"""Census API client for making HTTP requests to the US Census Bureau API."""

import os
from typing import Dict, Any, List, Optional
import httpx
from dotenv import load_dotenv

from .models import CensusResponse, COMMON_VARIABLES

# Load environment variables
load_dotenv()


class CensusAPIClient:
    """Client for interacting with the US Census Bureau API."""
    
    BASE_URL = "https://api.census.gov/data"
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Census API client.
        
        Args:
            api_key: Census API key. If not provided, reads from CENSUS_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("CENSUS_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Census API key is required. Set CENSUS_API_KEY environment variable "
                "or pass api_key parameter. Get your key at: "
                "https://api.census.gov/data/key_signup.html"
            )
        
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={"User-Agent": "US-Data-MCP-Census-Server/0.1.0"}
        )
    
    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    def _build_url(self, year: int, dataset: str) -> str:
        """Build Census API URL.
        
        Args:
            year: Year of data
            dataset: Dataset identifier (e.g., "acs/acs5")
            
        Returns:
            Complete API URL
        """
        return f"{self.BASE_URL}/{year}/{dataset}"
    
    def _build_params(
        self,
        variables: List[str],
        geography: str,
        state: Optional[str] = None,
        county: Optional[str] = None
    ) -> Dict[str, str]:
        """Build query parameters for Census API request.
        
        Args:
            variables: List of census variable codes
            geography: Geographic level
            state: State FIPS code (optional)
            county: County FIPS code (optional)
            
        Returns:
            Query parameters dict
        """
        params = {
            "get": ",".join(variables),
            "key": self.api_key
        }
        
        # Build geography parameter
        if county and state:
            params["for"] = f"county:{county}"
            params["in"] = f"state:{state}"
        elif state and geography.startswith("county"):
            params["for"] = "county:*"
            params["in"] = f"state:{state}"
        elif state:
            params["for"] = f"state:{state}"
        else:
            params["for"] = geography
        
        return params
    
    async def get_data(
        self,
        year: int,
        dataset: str,
        variables: List[str],
        geography: str,
        state: Optional[str] = None,
        county: Optional[str] = None
    ) -> CensusResponse:
        """Fetch data from Census API.
        
        Args:
            year: Year of data
            dataset: Dataset identifier
            variables: List of variable codes
            geography: Geographic level
            state: State FIPS code (optional)
            county: County FIPS code (optional)
            
        Returns:
            CensusResponse with data or error
        """
        try:
            url = self._build_url(year, dataset)
            params = self._build_params(variables, geography, state, county)
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Census API returns data as list of lists with first row as headers
            if len(data) < 2:
                return CensusResponse(
                    data=[],
                    metadata={
                        "year": year,
                        "dataset": dataset,
                        "variables": variables
                    },
                    success=True
                )
            
            headers = data[0]
            rows = data[1:]
            
            # Convert to list of dicts
            formatted_data = [
                dict(zip(headers, row)) for row in rows
            ]
            
            # Add variable descriptions
            metadata = {
                "year": year,
                "dataset": dataset,
                "variables": {
                    var: COMMON_VARIABLES.get(var, f"Variable {var}")
                    for var in variables
                },
                "count": len(formatted_data)
            }
            
            return CensusResponse(
                data=formatted_data,
                metadata=metadata,
                success=True
            )
            
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            return CensusResponse(
                data=[],
                metadata={"year": year, "dataset": dataset},
                success=False,
                error=error_msg
            )
        except Exception as e:
            return CensusResponse(
                data=[],
                metadata={"year": year, "dataset": dataset},
                success=False,
                error=str(e)
            )
    
    async def get_population_data(
        self,
        year: int,
        state: str,
        county: Optional[str] = None,
        variables: Optional[List[str]] = None
    ) -> CensusResponse:
        """Get population data for a geographic area.
        
        Args:
            year: Year of data
            state: State FIPS code
            county: County FIPS code (optional)
            variables: List of variable codes (uses defaults if not provided)
            
        Returns:
            CensusResponse with population data
        """
        if variables is None:
            variables = ["NAME", "B01001_001E", "B01002_001E"]  # Name, Total Pop, Median Age
        
        # Ensure NAME is included
        if "NAME" not in variables:
            variables = ["NAME"] + variables
        
        dataset = "acs/acs5"  # 5-year American Community Survey
        geography = "county:*" if county else f"state:{state}"
        
        return await self.get_data(
            year=year,
            dataset=dataset,
            variables=variables,
            geography=geography,
            state=state,
            county=county
        )
    
    async def get_economic_data(
        self,
        year: int,
        dataset: str = "acs/acs5",
        variables: Optional[List[str]] = None,
        geography: str = "state:*",
        state: Optional[str] = None
    ) -> CensusResponse:
        """Get economic data for a geographic area.
        
        Args:
            year: Year of data
            dataset: Dataset identifier
            variables: List of variable codes (uses defaults if not provided)
            geography: Geographic level
            state: State FIPS code (optional)
            
        Returns:
            CensusResponse with economic data
        """
        if variables is None:
            variables = [
                "NAME",
                "B19013_001E",  # Median Household Income
                "B17001_002E",  # Below Poverty Level
                "B23025_005E"   # Unemployment
            ]
        
        # Ensure NAME is included
        if "NAME" not in variables:
            variables = ["NAME"] + variables
        
        return await self.get_data(
            year=year,
            dataset=dataset,
            variables=variables,
            geography=geography,
            state=state
        )
    
    async def get_available_variables(self, year: int, dataset: str = "acs/acs5") -> Dict[str, Any]:
        """Get available variables for a dataset.
        
        Args:
            year: Year of data
            dataset: Dataset identifier
            
        Returns:
            Dict containing variable information
        """
        try:
            url = f"{self.BASE_URL}/{year}/{dataset}/variables.json"
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "common_variables": COMMON_VARIABLES}
