"""
Get air quality tool for Weather MCP Server.
"""

from typing import Dict, Any
from fastmcp import FastMCP
from datetime import datetime
from .common import BASE_URL, make_weather_request


def register_tool(mcp: FastMCP):
    """Register the get_air_quality tool with the FastMCP server."""

    @mcp.tool
    async def get_air_quality(
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """
        Get air quality data for a location.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate

        Returns:
            Dictionary containing air quality index and pollutant components
        """
        endpoint = f"{BASE_URL}/air_pollution"
        params = {
            "lat": latitude,
            "lon": longitude
        }

        result = await make_weather_request(endpoint, params)

        if not result["success"]:
            return result

        data = result["data"]

        aqi_levels = {
            1: "Good",
            2: "Fair",
            3: "Moderate",
            4: "Poor",
            5: "Very Poor"
        }

        air_data = data.get("list", [{}])[0]

        return {
            "success": True,
            "coordinates": {
                "latitude": latitude,
                "longitude": longitude
            },
            "air_quality_index": air_data.get("main", {}).get("aqi"),
            "aqi_level": aqi_levels.get(air_data.get("main", {}).get("aqi", 0), "Unknown"),
            "components": air_data.get("components", {}),
            "timestamp": datetime.fromtimestamp(air_data.get("dt", 0)).isoformat()
        }
