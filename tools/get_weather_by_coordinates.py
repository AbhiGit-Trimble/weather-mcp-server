"""
Get weather by coordinates tool for Weather MCP Server.
"""

from typing import Dict, Any
from fastmcp import FastMCP
from datetime import datetime
from .common import BASE_URL, make_weather_request


def register_tool(mcp: FastMCP):
    """Register the get_weather_by_coordinates tool with the FastMCP server."""

    @mcp.tool
    async def get_weather_by_coordinates(
        latitude: float,
        longitude: float,
        units: str = "metric"
    ) -> Dict[str, Any]:
        """
        Get current weather by latitude and longitude.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            units: Units of measurement - metric, imperial, or standard

        Returns:
            Dictionary containing current weather data for the coordinates
        """
        endpoint = f"{BASE_URL}/weather"
        params = {
            "lat": latitude,
            "lon": longitude,
            "units": units
        }

        result = await make_weather_request(endpoint, params)

        if not result["success"]:
            return result

        data = result["data"]

        return {
            "success": True,
            "location": {
                "name": data.get("name"),
                "country": data.get("sys", {}).get("country"),
                "coordinates": {
                    "latitude": latitude,
                    "longitude": longitude
                }
            },
            "current": {
                "temperature": data.get("main", {}).get("temp"),
                "feels_like": data.get("main", {}).get("feels_like"),
                "humidity": data.get("main", {}).get("humidity"),
                "pressure": data.get("main", {}).get("pressure"),
                "description": data.get("weather", [{}])[0].get("description"),
                "wind_speed": data.get("wind", {}).get("speed"),
                "clouds": data.get("clouds", {}).get("all")
            },
            "timestamp": datetime.fromtimestamp(data.get("dt", 0)).isoformat(),
            "units": units
        }
