"""FDA openFDA API client for accessing drug information, recalls, and adverse events."""

from typing import Dict, Any, List, Optional
from urllib.parse import quote
import httpx
from dotenv import load_dotenv

from .models import FDAResponse, RECALL_CLASSIFICATIONS

# Load environment variables
load_dotenv()


class FDAAPIClient:
    """Client for interacting with the FDA openFDA API.
    
    Note: openFDA API does not require an API key for basic usage.
    """
    
    BASE_URL = "https://api.fda.gov"
    
    def __init__(self):
        """Initialize FDA API client."""
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": "US-Data-MCP-FDA-Server/0.1.0"
            }
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
    
    def _build_search_query(self, **kwargs) -> str:
        """Build search query string from parameters.
        
        Args:
            **kwargs: Search parameters
            
        Returns:
            URL-encoded search query
        """
        conditions = []
        for key, value in kwargs.items():
            if value:
                # Escape special characters and build condition
                escaped_value = quote(str(value))
                conditions.append(f"{key}:{escaped_value}")
        
        return "+AND+".join(conditions) if conditions else ""
    
    async def search_drugs(
        self,
        brand_name: Optional[str] = None,
        generic_name: Optional[str] = None,
        application_number: Optional[str] = None,
        limit: int = 10
    ) -> FDAResponse:
        """Search for drug information.
        
        Args:
            brand_name: Brand/trade name
            generic_name: Generic/chemical name
            application_number: FDA application number
            limit: Maximum results
            
        Returns:
            FDAResponse with drug information
        """
        try:
            # Build search query
            search_params = {}
            if brand_name:
                search_params["openfda.brand_name"] = brand_name
            if generic_name:
                search_params["openfda.generic_name"] = generic_name
            if application_number:
                search_params["application_number"] = application_number
            
            if not search_params:
                return FDAResponse(
                    data=[],
                    metadata={},
                    success=False,
                    error="At least one search parameter is required"
                )
            
            search_query = self._build_search_query(**search_params)
            
            url = f"{self.BASE_URL}/drug/drugsfda.json"
            params = {
                "search": search_query,
                "limit": min(limit, 100)
            }
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", [])
            
            return FDAResponse(
                data=results,
                metadata={
                    "query": search_params,
                    "count": len(results),
                    "source": "drug/drugsfda"
                },
                success=True
            )
        
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text[:200]}"
            return FDAResponse(
                data=[],
                metadata={"query": locals()},
                success=False,
                error=error_msg
            )
        except Exception as e:
            return FDAResponse(
                data=[],
                metadata={"query": locals()},
                success=False,
                error=str(e)
            )
    
    async def search_drug_labels(
        self,
        brand_name: Optional[str] = None,
        generic_name: Optional[str] = None,
        limit: int = 10
    ) -> FDAResponse:
        """Search drug labeling information.
        
        Args:
            brand_name: Brand name
            generic_name: Generic name
            limit: Maximum results
            
        Returns:
            FDAResponse with drug label information
        """
        try:
            search_params = {}
            if brand_name:
                search_params["openfda.brand_name"] = brand_name
            if generic_name:
                search_params["openfda.generic_name"] = generic_name
            
            if not search_params:
                return FDAResponse(
                    data=[],
                    metadata={},
                    success=False,
                    error="Brand name or generic name is required"
                )
            
            search_query = self._build_search_query(**search_params)
            
            url = f"{self.BASE_URL}/drug/label.json"
            params = {
                "search": search_query,
                "limit": min(limit, 100)
            }
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", [])
            
            return FDAResponse(
                data=results,
                metadata={
                    "query": search_params,
                    "count": len(results),
                    "source": "drug/label"
                },
                success=True
            )
        
        except Exception as e:
            return FDAResponse(
                data=[],
                metadata={"query": locals()},
                success=False,
                error=str(e)
            )
    
    async def search_recalls(
        self,
        product_description: Optional[str] = None,
        classification: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 10
    ) -> FDAResponse:
        """Search drug recalls.
        
        Args:
            product_description: Product description
            classification: Recall classification (I, II, III)
            status: Recall status
            limit: Maximum results
            
        Returns:
            FDAResponse with recall information
        """
        try:
            search_params = {}
            if product_description:
                search_params["product_description"] = product_description
            if classification:
                search_params["classification"] = f"Class+{classification}"
            if status:
                search_params["status"] = status
            
            search_query = self._build_search_query(**search_params)
            
            url = f"{self.BASE_URL}/drug/enforcement.json"
            params = {}
            if search_query:
                params["search"] = search_query
            params["limit"] = min(limit, 100)
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", [])
            
            # Add classification descriptions
            for result in results:
                class_str = result.get("classification", "")
                if "Class I" in class_str:
                    result["classification_description"] = RECALL_CLASSIFICATIONS["I"]
                elif "Class II" in class_str:
                    result["classification_description"] = RECALL_CLASSIFICATIONS["II"]
                elif "Class III" in class_str:
                    result["classification_description"] = RECALL_CLASSIFICATIONS["III"]
            
            return FDAResponse(
                data=results,
                metadata={
                    "query": search_params,
                    "count": len(results),
                    "source": "drug/enforcement"
                },
                success=True
            )
        
        except Exception as e:
            return FDAResponse(
                data=[],
                metadata={"query": locals()},
                success=False,
                error=str(e)
            )
    
    async def search_adverse_events(
        self,
        drug_name: str,
        reaction: Optional[str] = None,
        limit: int = 10
    ) -> FDAResponse:
        """Search adverse event reports.
        
        Args:
            drug_name: Drug name
            reaction: Specific adverse reaction (optional)
            limit: Maximum results
            
        Returns:
            FDAResponse with adverse event data
        """
        try:
            search_params = {
                "patient.drug.openfda.brand_name": drug_name
            }
            
            if reaction:
                search_params["patient.reaction.reactionmeddrapt"] = reaction
            
            search_query = self._build_search_query(**search_params)
            
            url = f"{self.BASE_URL}/drug/event.json"
            params = {
                "search": search_query,
                "limit": min(limit, 100)
            }
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", [])
            
            return FDAResponse(
                data=results,
                metadata={
                    "drug_name": drug_name,
                    "reaction": reaction,
                    "count": len(results),
                    "source": "drug/event",
                    "note": "Data may include consumer and healthcare professional reports"
                },
                success=True
            )
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return FDAResponse(
                    data=[],
                    metadata={"drug_name": drug_name},
                    success=True,
                    error="No adverse events found for this drug"
                )
            error_msg = f"HTTP {e.response.status_code}: {e.response.text[:200]}"
            return FDAResponse(
                data=[],
                metadata={"drug_name": drug_name},
                success=False,
                error=error_msg
            )
        except Exception as e:
            return FDAResponse(
                data=[],
                metadata={"drug_name": drug_name},
                success=False,
                error=str(e)
            )
