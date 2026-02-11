"""Pydantic models for Census API requests and responses."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class PopulationSearchRequest(BaseModel):
    """Request model for population data search."""
    
    year: int = Field(..., description="Year of census data", ge=2000, le=2030)
    state: str = Field(..., description="State FIPS code (2 digits)", min_length=2, max_length=2)
    county: Optional[str] = Field(None, description="County FIPS code (3 digits)", min_length=3, max_length=3)
    variables: List[str] = Field(
        default=["NAME", "B01001_001E"],
        description="Census variables to retrieve (e.g., B01001_001E for total population)"
    )


class EconomicSearchRequest(BaseModel):
    """Request model for economic data search."""
    
    year: int = Field(..., description="Year of data", ge=2000, le=2030)
    dataset: str = Field(
        default="acs/acs5",
        description="Dataset name (e.g., 'acs/acs5' for 5-year American Community Survey)"
    )
    variables: List[str] = Field(
        default=["NAME", "B19013_001E"],
        description="Economic variables (e.g., B19013_001E for median household income)"
    )
    geography: str = Field(
        default="state:*",
        description="Geographic level (e.g., 'state:*', 'county:*')"
    )
    state: Optional[str] = Field(None, description="State FIPS code filter (2 digits)")


class CensusDataPoint(BaseModel):
    """Individual census data point."""
    
    name: str = Field(..., description="Geographic area name")
    value: Optional[str] = Field(None, description="Data value")
    variable: str = Field(..., description="Variable code")
    state: Optional[str] = Field(None, description="State FIPS code")
    county: Optional[str] = Field(None, description="County FIPS code")


class CensusResponse(BaseModel):
    """Response model for census data."""
    
    data: List[Dict[str, Any]] = Field(default_factory=list, description="Census data results")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Response metadata")
    success: bool = Field(default=True, description="Whether request was successful")
    error: Optional[str] = Field(None, description="Error message if request failed")


class CensusVariable(BaseModel):
    """Census variable metadata."""
    
    code: str = Field(..., description="Variable code (e.g., B01001_001E)")
    label: str = Field(..., description="Variable label/description")
    concept: str = Field(..., description="Concept/category")
    predicateType: Optional[str] = Field(None, description="Data type")


# Common Census Variables Reference
COMMON_VARIABLES = {
    # Population
    "B01001_001E": "Total Population",
    "B01002_001E": "Median Age",
    "B01003_001E": "Total Population (alternative)",
    
    # Economic
    "B19013_001E": "Median Household Income",
    "B19301_001E": "Per Capita Income",
    "B17001_002E": "Income Below Poverty Level",
    "B23025_005E": "Unemployment",
    
    # Housing
    "B25001_001E": "Total Housing Units",
    "B25002_002E": "Occupied Housing Units",
    "B25002_003E": "Vacant Housing Units",
    "B25077_001E": "Median Home Value",
    
    # Education
    "B15003_022E": "Bachelor's Degree",
    "B15003_023E": "Master's Degree",
    "B15003_024E": "Professional Degree",
    "B15003_025E": "Doctorate Degree",
    
    # Race & Ethnicity
    "B02001_002E": "White Alone",
    "B02001_003E": "Black or African American Alone",
    "B02001_004E": "American Indian and Alaska Native Alone",
    "B02001_005E": "Asian Alone",
    "B03001_003E": "Hispanic or Latino",
}
