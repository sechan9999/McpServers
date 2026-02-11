#!/usr/bin/env python3
"""
Example script demonstrating how to use the Census API client directly.
This can be used for testing without MCP.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path for import
sys.path.insert(0, str(Path(__file__).parent / "src" / "census-data" / "src"))

from us_data_mcp.census_data.api_client import CensusAPIClient


async def main():
    """Main demonstration function."""
    
    # Check for API key
    api_key = os.getenv("CENSUS_API_KEY")
    if not api_key:
        print("❌ Error: CENSUS_API_KEY environment variable not set")
        print("\nTo get an API key:")
        print("1. Visit https://api.census.gov/data/key_signup.html")
        print("2. Fill out the form")
        print("3. Check your email for the API key")
        print("\nThen set it:")
        print("  export CENSUS_API_KEY='your-key'  # Linux/macOS")
        print("  $env:CENSUS_API_KEY='your-key'    # Windows PowerShell")
        return
    
    print("🚀 US Census Bureau API Client Demo\n")
    print("=" * 60)
    
    # Initialize client
    async with CensusAPIClient(api_key=api_key) as client:
        
        # Example 1: Get population data for California
        print("\n📊 Example 1: California Population (2020)")
        print("-" * 60)
        
        result = await client.get_population_data(
            year=2020,
            state="06"  # California FIPS code
        )
        
        if result.success:
            print(f"✅ Success! Found {result.metadata['count']} result(s)")
            for data in result.data:
                print(f"\n  Location: {data.get('NAME')}")
                print(f"  Population: {data.get('B01001_001E', 'N/A'):,}")
                print(f"  Median Age: {data.get('B01002_001E', 'N/A')}")
        else:
            print(f"❌ Error: {result.error}")
        
        # Example 2: Get economic data for multiple states
        print("\n\n💰 Example 2: Economic Data for Top 3 States (2021)")
        print("-" * 60)
        
        states = [
            ("06", "California"),
            ("48", "Texas"),
            ("12", "Florida")
        ]
        
        for state_code, state_name in states:
            result = await client.get_economic_data(
                year=2021,
                state=state_code,
                geography=f"state:{state_code}"
            )
            
            if result.success and result.data:
                data = result.data[0]
                income = data.get('B19013_001E', 'N/A')
                poverty = data.get('B17001_002E', 'N/A')
                unemployment = data.get('B23025_005E', 'N/A')
                
                print(f"\n  {state_name}:")
                print(f"    Median Household Income: ${income}")
                print(f"    Below Poverty Level: {poverty}")
                print(f"    Unemployed: {unemployment}")
        
        # Example 3: Show common variables
        print("\n\n📋 Example 3: Common Census Variables")
        print("-" * 60)
        
        from us_data_mcp.census_data.models import COMMON_VARIABLES
        
        categories = {
            "Population": [],
            "Economic": [],
            "Housing": [],
            "Education": []
        }
        
        for code, label in COMMON_VARIABLES.items():
            if "Population" in label or "Age" in label:
                categories["Population"].append((code, label))
            elif any(word in label for word in ["Income", "Poverty", "Unemployment"]):
                categories["Economic"].append((code, label))
            elif "Housing" in label or "Home" in label:
                categories["Housing"].append((code, label))
            elif "Degree" in label:
                categories["Education"].append((code, label))
        
        for category, variables in categories.items():
            if variables:
                print(f"\n  {category}:")
                for code, label in variables[:3]:  # Show first 3 of each category
                    print(f"    {code}: {label}")
        
    print("\n\n" + "=" * 60)
    print("✨ Demo complete!")
    print("\nNext steps:")
    print("1. Try modifying the examples above")
    print("2. Explore more variables from COMMON_VARIABLES")
    print("3. Use with Claude Desktop or Cline via MCP")
    print("\nSee QUICKSTART.md for more information!")


if __name__ == "__main__":
    asyncio.run(main())
