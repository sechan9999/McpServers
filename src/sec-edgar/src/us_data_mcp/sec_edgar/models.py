"""Pydantic models for SEC EDGAR API requests and responses."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class CompanySearchRequest(BaseModel):
    """Request model for company search."""
    
    query: str = Field(..., description="Company name, ticker symbol, or CIK")
    

class FilingsRequest(BaseModel):
    """Request model for company filings."""
    
    cik: str = Field(..., description="Central Index Key (CIK) - 10 digits with leading zeros")
    form_type: Optional[str] = Field(None, description="Filing type (10-K, 10-Q, 8-K, etc.)")
    count: int = Field(default=10, description="Number of filings to retrieve", ge=1, le=100)


class FilingContentRequest(BaseModel):
    """Request model for filing content."""
    
    cik: str = Field(..., description="Central Index Key (CIK)")
    accession_number: str = Field(..., description="Filing accession number (e.g., 0001234567-23-012345)")


class CompanyInfo(BaseModel):
    """Company information model."""
    
    cik: str = Field(..., description="Central Index Key")
    name: str = Field(..., description="Company name")
    ticker: Optional[str] = Field(None, description="Stock ticker symbol")
    exchange: Optional[str] = Field(None, description="Stock exchange")
    sic: Optional[str] = Field(None, description="SIC code")
    sic_description: Optional[str] = Field(None, description="SIC description")
    category: Optional[str] = Field(None, description="Company category")


class Filing(BaseModel):
    """Filing information model."""
    
    accession_number: str = Field(..., description="Accession number")
    filing_date: str = Field(..., description="Filing date (YYYY-MM-DD)")
    report_date: Optional[str] = Field(None, description="Report date")
    form_type: str = Field(..., description="Form type (10-K, 10-Q, etc.)")
    file_number: Optional[str] = Field(None, description="File number")
    items: Optional[str] = Field(None, description="Items (for 8-K)")
    description: Optional[str] = Field(None, description="Filing description")
    primary_document: Optional[str] = Field(None, description="Primary document filename")
    primary_doc_description: Optional[str] = Field(None, description="Primary document description")


class SECResponse(BaseModel):
    """Response model for SEC data."""
    
    data: List[Dict[str, Any]] = Field(default_factory=list, description="SEC data results")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Response metadata")
    success: bool = Field(default=True, description="Whether request was successful")
    error: Optional[str] = Field(None, description="Error message if request failed")


# Common SEC Form Types
COMMON_FORM_TYPES = {
    # Annual & Quarterly Reports
    "10-K": "Annual Report",
    "10-Q": "Quarterly Report",
    "8-K": "Current Report (major events)",
    "10-K/A": "Annual Report Amendment",
    "10-Q/A": "Quarterly Report Amendment",
    
    # Registration & Offerings
    "S-1": "Registration Statement",
    "S-3": "Registration Statement (simplified)",
    "S-4": "Registration Statement (business combinations)",
    "S-8": "Registration Statement (employee benefit plans)",
    "424B": "Prospectus",
    
    # Proxy Materials
    "DEF 14A": "Definitive Proxy Statement",
    "PRE 14A": "Preliminary Proxy Statement",
    "DEFA14A": "Additional Proxy Soliciting Materials",
    
    # Ownership Reports
    "3": "Initial Statement of Beneficial Ownership",
    "4": "Statement of Changes in Beneficial Ownership",
    "5": "Annual Statement of Changes in Beneficial Ownership",
    "13F-HR": "Institutional Investment Manager Holdings Report",
    "13D": "Schedule 13D - Beneficial Ownership Report",
    "13G": "Schedule 13G - Beneficial Ownership Report (passive)",
    
    # Tender Offers
    "SC 13D": "Tender Offer Statement",
    "SC 13G": "Tender Offer Statement (passive)",
    "SC TO": "Tender Offer Statement",
    
    # Foreign Companies
    "20-F": "Annual Report (foreign private issuers)",
    "6-K": "Current Report (foreign private issuers)",
    
    # Investment Companies
    "N-CSR": "Certified Shareholder Report (investment companies)",
    "N-Q": "Quarterly Schedule of Investments",
    "485BPOS": "Post-Effective Amendment (investment companies)",
}

# Major SIC Industry Categories
SIC_CATEGORIES = {
    "0100-0999": "Agriculture, Forestry, and Fishing",
    "1000-1499": "Mining",
    "1500-1799": "Construction",
    "2000-3999": "Manufacturing",
    "4000-4999": "Transportation, Communications, Electric, Gas, and Sanitary Services",
    "5000-5199": "Wholesale Trade",
    "5200-5999": "Retail Trade",
    "6000-6799": "Finance, Insurance, and Real Estate",
    "7000-8999": "Services",
    "9100-9729": "Public Administration",
}
