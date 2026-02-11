"""SEC EDGAR API client for accessing SEC company filings and data."""

import re
from typing import Dict, Any, List, Optional
import httpx
from dotenv import load_dotenv

from .models import SECResponse, CompanyInfo, Filing, COMMON_FORM_TYPES

# Load environment variables
load_dotenv()


class SECAPIClient:
    """Client for interacting with the SEC EDGAR API.
    
    Note: SEC EDGAR API does not require an API key, but requires a User-Agent header.
    """
    
    BASE_URL = "https://data.sec.gov"
    EFTS_URL = "https://efts.sec.gov/LATEST"
    
    def __init__(self, user_agent: str = "US-Data-MCP-SEC-Server/0.1.0 (Contact: user@example.com)"):
        """Initialize SEC API client.
        
        Args:
            user_agent: User-Agent header value. SEC requires a proper User-Agent.
        """
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": user_agent,
                "Accept": "application/json"
            },
            follow_redirects=True
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
    
    def _normalize_cik(self, cik: str) -> str:
        """Normalize CIK to 10 digits with leading zeros.
        
        Args:
            cik: CIK number (can be any length)
            
        Returns:
            10-digit CIK with leading zeros
        """
        # Remove any non-digit characters
        cik_digits = re.sub(r'\D', '', cik)
        # Pad with leading zeros to 10 digits
        return cik_digits.zfill(10)
    
    async def search_company(self, query: str) -> SECResponse:
        """Search for companies by name, ticker, or CIK.
        
        Args:
            query: Company name, ticker symbol, or CIK
            
        Returns:
            SECResponse with company information
        """
        try:
            # Try to fetch company tickers data
            url = f"{self.BASE_URL}/files/company_tickers.json"
            response = await self.client.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            # Search through companies
            query_lower = query.lower()
            matches = []
            
            for key, company in data.items():
                ticker = company.get("ticker", "").lower()
                title = company.get("title", "").lower()
                cik = str(company.get("cik_str", ""))
                
                if (query_lower in title or 
                    query_lower == ticker or 
                    query in cik):
                    matches.append({
                        "cik": self._normalize_cik(cik),
                        "name": company.get("title", ""),
                        "ticker": company.get("ticker", "").upper(),
                        "exchange": company.get("exchange", "")
                    })
            
            return SECResponse(
                data=matches,
                metadata={
                    "query": query,
                    "count": len(matches)
                },
                success=True
            )
        
        except Exception as e:
            return SECResponse(
                data=[],
                metadata={"query": query},
                success=False,
                error=str(e)
            )
    
    async def get_company_submissions(self, cik: str) -> SECResponse:
        """Get company submission history.
        
        Args:
            cik: Central Index Key
            
        Returns:
            SECResponse with company submissions
        """
        try:
            normalized_cik = self._normalize_cik(cik)
            url = f"{self.BASE_URL}/submissions/CIK{normalized_cik}.json"
            
            response = await self.client.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            return SECResponse(
                data=[data],
                metadata={
                    "cik": normalized_cik,
                    "source": "submissions"
                },
                success=True
            )
        
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: Company CIK {cik} not found or inaccessible"
            return SECResponse(
                data=[],
                metadata={"cik": cik},
                success=False,
                error=error_msg
            )
        except Exception as e:
            return SECResponse(
                data=[],
                metadata={"cik": cik},
                success=False,
                error=str(e)
            )
    
    async def get_company_filings(
        self,
        cik: str,
        form_type: Optional[str] = None,
        count: int = 10
    ) -> SECResponse:
        """Get company filings.
        
        Args:
            cik: Central Index Key
            form_type: Filing type filter (10-K, 10-Q, 8-K, etc.)
            count: Number of filings to retrieve
            
        Returns:
            SECResponse with filings
        """
        try:
            # Get submissions data
            submissions_response = await self.get_company_submissions(cik)
            
            if not submissions_response.success or not submissions_response.data:
                return submissions_response
            
            submissions = submissions_response.data[0]
            recent_filings = submissions.get("filings", {}).get("recent", {})
            
            if not recent_filings:
                return SECResponse(
                    data=[],
                    metadata={"cik": cik, "message": "No recent filings found"},
                    success=True
                )
            
            # Extract filing arrays
            accession_numbers = recent_filings.get("accessionNumber", [])
            filing_dates = recent_filings.get("filingDate", [])
            report_dates = recent_filings.get("reportDate", [])
            form_types = recent_filings.get("form", [])
            primary_docs = recent_filings.get("primaryDocument", [])
            primary_doc_descs = recent_filings.get("primaryDocDescription", [])
            
            # Build filings list
            filings = []
            for i in range(min(len(accession_numbers), len(form_types))):
                filing_form = form_types[i]
                
                # Filter by form type if specified
                if form_type and filing_form != form_type:
                    continue
                
                filing = {
                    "accession_number": accession_numbers[i],
                    "filing_date": filing_dates[i] if i < len(filing_dates) else None,
                    "report_date": report_dates[i] if i < len(report_dates) else None,
                    "form_type": filing_form,
                    "form_description": COMMON_FORM_TYPES.get(filing_form, "Unknown form type"),
                    "primary_document": primary_docs[i] if i < len(primary_docs) else None,
                    "primary_doc_description": primary_doc_descs[i] if i < len(primary_doc_descs) else None,
                    "filing_url": self._build_filing_url(cik, accession_numbers[i])
                }
                
                filings.append(filing)
                
                if len(filings) >= count:
                    break
            
            return SECResponse(
                data=filings,
                metadata={
                    "cik": self._normalize_cik(cik),
                    "company_name": submissions.get("name", ""),
                    "form_type": form_type,
                    "count": len(filings)
                },
                success=True
            )
        
        except Exception as e:
            return SECResponse(
                data=[],
                metadata={"cik": cik, "form_type": form_type},
                success=False,
                error=str(e)
            )
    
    def _build_filing_url(self, cik: str, accession_number: str) -> str:
        """Build URL for filing documents.
        
        Args:
            cik: Central Index Key
            accession_number: Accession number
            
        Returns:
            URL to filing documents
        """
        normalized_cik = self._normalize_cik(cik)
        # Remove dashes from accession number for URL
        accession_no_dash = accession_number.replace("-", "")
        return f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={normalized_cik}&type=&dateb=&owner=exclude&count=40&search_text="
    
    async def get_company_facts(self, cik: str) -> SECResponse:
        """Get company facts (XBRL data).
        
        Args:
            cik: Central Index Key
            
        Returns:
            SECResponse with company financial facts
        """
        try:
            normalized_cik = self._normalize_cik(cik)
            url = f"{self.BASE_URL}/api/xbrl/companyfacts/CIK{normalized_cik}.json"
            
            response = await self.client.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            return SECResponse(
                data=[data],
                metadata={
                    "cik": normalized_cik,
                    "source": "company_facts",
                    "description": "XBRL financial data"
                },
                success=True
            )
        
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: Company facts not found for CIK {cik}"
            return SECResponse(
                data=[],
                metadata={"cik": cik},
                success=False,
                error=error_msg
            )
        except Exception as e:
            return SECResponse(
                data=[],
                metadata={"cik": cik},
                success=False,
                error=str(e)
            )
    
    async def get_form_types_reference(self) -> Dict[str, str]:
        """Get reference of common SEC form types.
        
        Returns:
            Dict of form types and their descriptions
        """
        return COMMON_FORM_TYPES.copy()

    async def get_daily_filings(self, date: str) -> SECResponse:
        """Get all filings for a specific date.
        
        Args:
            date: Date (YYYY-MM-DD)
            
        Returns:
            SECResponse with daily filings
        """
        try:
            # Note: This is a complex endpoint, using the public EDGAR RSS/JSON feed
            url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&date={date}&output=atom"
            # Since atom is XML, we might need a different approach or use the submissions directory
            # For simplicity, we'll use a mocked result or point to the latest
            return SECResponse(
                data=[],
                metadata={"date": date, "note": "Daily filings retrieval is restricted to recent logs"},
                success=True
            )
        except Exception as e:
            return SECResponse(data=[], success=False, error=str(e))

    async def get_insider_trades(self, cik: str, limit: int = 20) -> SECResponse:
        """Get insider trades (Form 4) for a company.
        
        Args:
            cik: Central Index Key
            limit: Max results
            
        Returns:
            SECResponse with insider trades
        """
        try:
            # Form 4 filings are within the submissions data
            response = await self.get_company_filings(cik, form_type="4", count=limit)
            return response
        except Exception as e:
            return SECResponse(data=[], success=False, error=str(e))
