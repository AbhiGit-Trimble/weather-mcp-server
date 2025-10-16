"""
Get weather forecast tool for Weather MCP Server.
"""

from typing import Dict, Any
from fastmcp import FastMCP
from datetime import datetime
from .common import BASE_URL, make_weather_request


def register_tool(mcp: FastMCP):
    """Register the get_forecast tool with the FastMCP server."""

    @mcp.tool
    async def get_forecast(
        location: str,
        units: str = "metric",
        days: int = 5
    ) -> Dict[str, Any]:
        """
        Get 5-day weather forecast with 3-hour intervals.

        Args:
            location: City name, state code, and country code
            units: Units of measurement - metric, imperial, or standard
            days: Number of days to forecast (1-5)

        Returns:
            Dictionary containing forecast data with temperature, description, humidity, etc.
        """
        endpoint = f"{BASE_URL}/forecast"
        params = {
            "q": location,
            "units": units,
            "cnt": min(days, 5) * 8  # 8 intervals per day (3-hour intervals)
        }

        result = await make_weather_request(endpoint, params)

        if not result["success"]:
            return result

        data = result["data"]

        forecasts = []
        for item in data.get("list", []):
            forecasts.append({
                "datetime": datetime.fromtimestamp(item.get("dt", 0)).isoformat(),
                "temperature": item.get("main", {}).get("temp"),
                "feels_like": item.get("main", {}).get("feels_like"),
                "temp_min": item.get("main", {}).get("temp_min"),
                "temp_max": item.get("main", {}).get("temp_max"),
                "pressure": item.get("main", {}).get("pressure"),
                "humidity": item.get("main", {}).get("humidity"),
                "description": item.get("weather", [{}])[0].get("description"),
                "icon": item.get("weather", [{}])[0].get("icon"),
                "wind_speed": item.get("wind", {}).get("speed"),
                "clouds": item.get("clouds", {}).get("all"),
                "pop": item.get("pop", 0)  # Probability of precipitation
            })

        return {
            "success": True,
            "location": {
                "name": data.get("city", {}).get("name"),
                "country": data.get("city", {}).get("country"),
                "coordinates": {
                    "latitude": data.get("city", {}).get("coord", {}).get("lat"),
                    "longitude": data.get("city", {}).get("coord", {}).get("lon")
                }
            },
            "forecast": forecasts,
            "units": units
        }
