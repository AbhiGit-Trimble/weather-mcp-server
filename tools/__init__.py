"""
Tools package for the Weather MCP server.

This package contains individual tool modules that can be registered with the FastMCP server.
Each tool module has a register_tool function that takes a FastMCP instance and registers
the tool with it.
"""

from fastmcp import FastMCP
from . import (
    get_current_weather,
    get_forecast,
    search_location,
    get_weather_by_coordinates,
    get_air_quality,
    compare_weather
)


def register_all_tools(mcp: FastMCP):
    """
    Register all tools with the FastMCP server.

    Args:
        mcp: The FastMCP server instance to register tools with
    """
    get_current_weather.register_tool(mcp)
    get_forecast.register_tool(mcp)
    search_location.register_tool(mcp)
    get_weather_by_coordinates.register_tool(mcp)
    get_air_quality.register_tool(mcp)
    compare_weather.register_tool(mcp)


__all__ = [
    "register_all_tools",
    "get_current_weather",
    "get_forecast",
    "search_location",
    "get_weather_by_coordinates",
    "get_air_quality",
    "compare_weather"
]
