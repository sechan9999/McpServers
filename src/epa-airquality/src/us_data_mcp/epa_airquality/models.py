"""Pydantic models for EPA AQS API requests and responses."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class AQSSearchRequest(BaseModel):
    """Request model for EPA AQS data search."""
    
    param_code: str = Field(..., description="Parameter code (e.g., 44201 for Ozone, 88101 for PM2.5)")
    bdate: str = Field(..., description="Begin date (YYYYMMDD)")
    edate: str = Field(..., description="End date (YYYYMMDD)")
    state: str = Field(..., description="State FIPS code (2 digits)")
    county: Optional[str] = Field(None, description="County FIPS code (3 digits)")


class EPAResponse(BaseModel):
    """Response model for EPA data."""
    
    data: List[Dict[str, Any]] = Field(default_factory=list, description="AQS data results")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Response metadata")
    success: bool = Field(default=True, description="Whether request was successful")
    error: Optional[str] = Field(None, description="Error message if request failed")


# Common AQS Parameter Codes
COMMON_PARAMS = {
    "44201": "Ozone",
    "42401": "Sulfur dioxide",
    "42101": "Carbon monoxide",
    "42602": "Nitrogen dioxide (NO2)",
    "81102": "PM10 Total 0-10um",
    "88101": "PM2.5 - Local Conditions",
    "88502": "Acceptable PM2.5 AQI Specs",
    "14129": "Lead (TSP) LC"
}
