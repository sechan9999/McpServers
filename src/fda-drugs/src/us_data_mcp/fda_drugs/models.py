"""Pydantic models for FDA openFDA API requests and responses."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class DrugSearchRequest(BaseModel):
    """Request model for drug search."""
    
    brand_name: Optional[str] = Field(None, description="Brand/trade name of the drug")
    generic_name: Optional[str] = Field(None, description="Generic/chemical name of the drug")
    application_number: Optional[str] = Field(None, description="FDA application number")
    limit: int = Field(default=10, description="Maximum number of results", ge=1, le=100)


class RecallSearchRequest(BaseModel):
    """Request model for drug recall search."""
    
    product_description: Optional[str] = Field(None, description="Product description or name")
    classification: Optional[str] = Field(None, description="Recall classification (I, II, III)")
    status: Optional[str] = Field(None, description="Recall status (Ongoing, Completed, Terminated)")
    limit: int = Field(default=10, description="Maximum number of results", ge=1, le=100)


class AdverseEventRequest(BaseModel):
    """Request model for adverse event search."""
    
    drug_name: str = Field(..., description="Drug name to search for adverse events")
    reaction: Optional[str] = Field(None, description="Specific adverse reaction/side effect")
    limit: int = Field(default=10, description="Maximum number of results", ge=1, le=100)


class FDAResponse(BaseModel):
    """Response model for FDA data."""
    
    data: List[Dict[str, Any]] = Field(default_factory=list, description="FDA data results")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Response metadata")
    success: bool = Field(default=True, description="Whether request was successful")
    error: Optional[str] = Field(None, description="Error message if request failed")


# Recall Classifications
RECALL_CLASSIFICATIONS = {
    "I": "Class I - Dangerous or defective products that predictably could cause serious health problems or death",
    "II": "Class II - Products that might cause a temporary health problem, or pose a slight threat of a serious nature",
    "III": "Class III - Products unlikely to cause any adverse health reaction, but violate FDA labeling or manufacturing regulations"
}

# Common Drug Routes
DRUG_ROUTES = [
    "ORAL",
    "INTRAVENOUS",
    "TOPICAL",
    "INTRAMUSCULAR",
    "SUBCUTANEOUS",
    "INHALATION",
    "OPHTHALMIC",
    "TRANSDERMAL",
    "RECTAL",
    "NASAL"
]

# Drug Product Types
PRODUCT_TYPES = {
    "HUMAN PRESCRIPTION DRUG": "Prescription medications for human use",
    "HUMAN OTC DRUG": "Over-the-counter medications for human use",
    "VACCINE": "Vaccines and immunizations",
    "PLASMA DERIVATIVE": "Products derived from human plasma",
    "CELLULAR THERAPY": "Cell-based therapeutic products",
    "STANDARDIZED ALLERGENIC": "Standardized allergy products"
}

# Common Adverse Reactions (for reference)
COMMON_ADVERSE_REACTIONS = [
    "nausea",
    "headache",
    "dizziness",
    "fatigue",
    "diarrhea",
    "vomiting",
    "rash",
    "pruritus",  # itching
    "insomnia",
    "anxiety",
    "depression",
    "pain",
    "fever",
    "cough",
    "dyspnea"  # shortness of breath
]
