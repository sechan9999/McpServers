"""EPA AQS API client for accessing air quality data."""

import os
from typing import Dict, Any, List, Optional
import httpx
from dotenv import load_dotenv

from .models import EPAResponse, COMMON_PARAMS

# Load environment variables
load_dotenv()


class EPAAQSClient:
    """Client for interacting with the EPA AQS (Air Quality System) API."""
    
    BASE_URL = "https://aqs.epa.gov/data/api"
    
    def __init__(self, email: Optional[str] = None, api_key: Optional[str] = None):
        """Initialize EPA AQS client.
        
        Args:
            email: Registered email for AQS API
            api_key: AQS API key
        """
        self.email = email or os.getenv("EPA_AQS_EMAIL")
        self.api_key = api_key or os.getenv("EPA_AQS_KEY")
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def get_daily_data(
        self,
        param_code: str,
        bdate: str,
        edate: str,
        state: str,
        county: Optional[str] = None
    ) -> EPAResponse:
        """Fetch daily summaries from EPA AQS API.
        
        Args:
            param_code: Parameter code
            bdate: Begin date (YYYYMMDD)
            edate: End date (YYYYMMDD)
            state: State FIPS code
            county: County FIPS code (optional)
            
        Returns:
            EPAResponse with data
        """
        if not self.email or not self.api_key:
            return EPAResponse(
                success=False,
                error="EPA AQS email and API key are required. Sign up at https://aqs.epa.gov/data/api/signup"
            )
            
        try:
            endpoint = "/dailyData/byCounty" if county else "/dailyData/byState"
            params = {
                "email": self.email,
                "key": self.api_key,
                "param": param_code,
                "bdate": bdate,
                "edate": edate,
                "state": state
            }
            if county:
                params["county"] = county
                
            response = await self.client.get(f"{self.BASE_URL}{endpoint}", params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("Header", [{}])[0].get("status") != "Success":
                return EPAResponse(
                    success=False,
                    error=data.get("Header", [{}])[0].get("error_msg", "Unknown AQS error")
                )
                
            results = data.get("Data", [])
            return EPAResponse(
                data=results,
                metadata={
                    "param": param_code,
                    "param_description": COMMON_PARAMS.get(param_code, "Unknown"),
                    "count": len(results)
                },
                success=True
            )
            
        except Exception as e:
            return EPAResponse(
                success=False,
                error=str(e)
            )

    async def get_common_params(self) -> Dict[str, str]:
        """Return common AQS parameter codes."""
        return COMMON_PARAMS.copy()
