"""
Search location tool for Weather MCP Server.
"""

from typing import Dict, Any
from fastmcp import FastMCP
from .common import GEO_URL, make_weather_request


def register_tool(mcp: FastMCP):
    """Register the search_location tool with the FastMCP server."""

    @mcp.tool
    async def search_location(
        query: str,
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        Search for a location and get its coordinates.

        Args:
            query: Location name to search for
            limit: Maximum number of results (max 10)

        Returns:
            Dictionary containing list of matching locations with coordinates
        """
        endpoint = f"{GEO_URL}/direct"
        params = {
            "q": query,
            "limit": min(limit, 10)
        }

        result = await make_weather_request(endpoint, params)

        if not result["success"]:
            return result

        data = result["data"]

        locations = []
        for item in data:
            locations.append({
                "name": item.get("name"),
                "local_names": item.get("local_names", {}),
                "country": item.get("country"),
                "state": item.get("state"),
                "coordinates": {
                    "latitude": item.get("lat"),
                    "longitude": item.get("lon")
                }
            })

        return {
            "success": True,
            "query": query,
            "results": locations,
            "count": len(locations)
        }
