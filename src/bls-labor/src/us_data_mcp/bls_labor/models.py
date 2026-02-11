"""Pydantic models for BLS API requests and responses."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class BLSSeriesRequest(BaseModel):
    """Request model for BLS series data."""
    
    series_ids: List[str] = Field(..., description="List of BLS series IDs (e.g., LAUCT060370000000003 for LA County unemployment)")
    start_year: Optional[int] = Field(None, description="Start year for data")
    end_year: Optional[int] = Field(None, description="End year for data")
    registration_key: Optional[str] = Field(None, description="BLS registration key (optional, can use BLS_API_KEY env)")


class BLSResponse(BaseModel):
    """Response model for BLS data."""
    
    status: str = Field(..., description="Request status")
    data: List[Dict[str, Any]] = Field(default_factory=list, description="Series data results")
    message: Optional[List[str]] = Field(None, description="API messages or warnings")
    success: bool = Field(default=True, description="Whether request was successful")
    error: Optional[str] = Field(None, description="Error message if request failed")


# Common BLS Series IDs
COMMON_SERIES = {
    # Unemployment
    "LNS14000000": "Unemployment Rate (Seasonally Adjusted) - National",
    "LNS14000001": "Unemployment Rate - Men",
    "LNS14000002": "Unemployment Rate - Women",
    
    # CPI (Inflation)
    "CUUR0000SA0": "CPI for All Urban Consumers (All Items) - U.S. City Average",
    "CUUR0000SAF1": "CPI - Food",
    "CUUR0000SA0E": "CPI - Energy",
    
    # Employment
    "CES0000000001": "Total Nonfarm Employment (Seasonally Adjusted)",
    "CES0500000003": "Average Hourly Earnings of All Private Employees",
    
    # Productivity
    "PRU8010663": "Labor Productivity - Nonfarm Business"
}
