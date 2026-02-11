"""BLS API client for accessing Bureau of Labor Statistics data."""

import os
from typing import Dict, Any, List, Optional
import httpx
from dotenv import load_dotenv

from .models import BLSResponse, COMMON_SERIES

# Load environment variables
load_dotenv()


class BLSAPIClient:
    """Client for interacting with the Bureau of Labor Statistics (BLS) API."""
    
    BASE_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize BLS API client.
        
        Args:
            api_key: BLS API key. If not provided, reads from BLS_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("BLS_API_KEY")
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={"Content-Type": "application/json"}
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
    
    async def get_series_data(
        self,
        series_ids: List[str],
        start_year: Optional[int] = None,
        end_year: Optional[int] = None
    ) -> BLSResponse:
        """Fetch data for one or more BLS series.
        
        Args:
            series_ids: List of BLS series IDs
            start_year: Start year (optional)
            end_year: End year (optional)
            
        Returns:
            BLSResponse with data
        """
        try:
            payload = {
                "seriesid": series_ids
            }
            
            if start_year:
                payload["startyear"] = str(start_year)
            if end_year:
                payload["endyear"] = str(end_year)
            if self.api_key:
                payload["registrationkey"] = self.api_key
                
            response = await self.client.post(self.BASE_URL, json=payload)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") == "REQUEST_NOT_PROCESSED":
                return BLSResponse(
                    status="FAIL",
                    success=False,
                    error=data.get("message", ["Unknown API error"])[0]
                )
            
            results = data.get("Results", {}).get("series", [])
            
            # Add descriptions from common series if available
            for series in results:
                s_id = series.get("seriesID")
                if s_id in COMMON_SERIES:
                    series["description"] = COMMON_SERIES[s_id]
            
            return BLSResponse(
                status=data.get("status", "OK"),
                data=results,
                message=data.get("message"),
                success=True
            )
            
        except Exception as e:
            return BLSResponse(
                status="ERROR",
                success=False,
                error=str(e)
            )

    async def get_common_series(self) -> Dict[str, str]:
        """Return common series IDs and descriptions."""
        return COMMON_SERIES.copy()
