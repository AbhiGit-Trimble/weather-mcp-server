"""
Compare weather tool for Weather MCP Server.
"""

from typing import Dict, Any, List
from fastmcp import FastMCP
from datetime import datetime
from .common import BASE_URL, make_weather_request


def register_tool(mcp: FastMCP):
    """Register the compare_weather tool with the FastMCP server."""

    @mcp.tool
    async def compare_weather(
        locations: List[str],
        units: str = "metric"
    ) -> Dict[str, Any]:
        """
        Compare current weather between multiple locations.

        Args:
            locations: List of city names to compare (2-5 cities)
            units: Units of measurement - metric, imperial, or standard

        Returns:
            Dictionary containing weather comparison data for all locations
        """
        if len(locations) < 2:
            return {
                "success": False,
                "error": "Please provide at least 2 locations to compare"
            }

        if len(locations) > 5:
            return {
                "success": False,
                "error": "Maximum 5 locations allowed for comparison"
            }

        comparisons = []
        for location in locations:
            endpoint = f"{BASE_URL}/weather"
            params = {"q": location, "units": units}

            result = await make_weather_request(endpoint, params)

            if result["success"]:
                data = result["data"]
                comparisons.append({
                    "location": {
                        "name": data.get("name"),
                        "country": data.get("sys", {}).get("country")
                    },
                    "current": {
                        "temperature": data.get("main", {}).get("temp"),
                        "feels_like": data.get("main", {}).get("feels_like"),
                        "humidity": data.get("main", {}).get("humidity"),
                        "description": data.get("weather", [{}])[0].get("description"),
                        "wind_speed": data.get("wind", {}).get("speed")
                    }
                })
            else:
                comparisons.append({
                    "location": location,
                    "error": result.get("error", "Failed to fetch weather data")
                })

        return {
            "success": True,
            "locations": comparisons,
            "units": units,
            "comparison_time": datetime.now().isoformat()
        }
