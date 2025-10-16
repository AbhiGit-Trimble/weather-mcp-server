"""
Get current weather tool for Weather MCP Server.
"""

from typing import Dict, Any
from fastmcp import FastMCP
from datetime import datetime
from .common import BASE_URL, make_weather_request


def register_tool(mcp: FastMCP):
    """Register the get_current_weather tool with the FastMCP server."""

    @mcp.tool
    async def get_current_weather(
        location: str,
        units: str = "metric"
    ) -> Dict[str, Any]:
        """
        Get current weather conditions for a specific location.

        Args:
            location: City name, state code, and country code (e.g., 'London,UK' or 'New York,NY,US')
            units: Units of measurement - metric (Celsius), imperial (Fahrenheit), or standard (Kelvin)

        Returns:
            Dictionary containing current weather data with location, temperature, humidity, etc.
        """
        endpoint = f"{BASE_URL}/weather"
        params = {"q": location, "units": units}

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
                    "latitude": data.get("coord", {}).get("lat"),
                    "longitude": data.get("coord", {}).get("lon")
                }
            },
            "current": {
                "temperature": data.get("main", {}).get("temp"),
                "feels_like": data.get("main", {}).get("feels_like"),
                "temp_min": data.get("main", {}).get("temp_min"),
                "temp_max": data.get("main", {}).get("temp_max"),
                "pressure": data.get("main", {}).get("pressure"),
                "humidity": data.get("main", {}).get("humidity"),
                "description": data.get("weather", [{}])[0].get("description"),
                "icon": data.get("weather", [{}])[0].get("icon"),
                "wind": {
                    "speed": data.get("wind", {}).get("speed"),
                    "direction": data.get("wind", {}).get("deg")
                },
                "clouds": data.get("clouds", {}).get("all"),
                "visibility": data.get("visibility")
            },
            "timestamp": datetime.fromtimestamp(data.get("dt", 0)).isoformat(),
            "sunrise": datetime.fromtimestamp(data.get("sys", {}).get("sunrise", 0)).isoformat(),
            "sunset": datetime.fromtimestamp(data.get("sys", {}).get("sunset", 0)).isoformat(),
            "units": units
        }
