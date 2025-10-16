#!/usr/bin/env python3
"""
Weather MCP Server
A Model Context Protocol server for accessing weather data from OpenWeatherMap API
"""

import asyncio
import json
import os
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel,
)
import mcp.types as types


class WeatherMCPServer:
    """MCP Server for Weather Data"""
    
    def __init__(self):
        self.server = Server("weather-mcp-server")
        self.api_key = os.getenv("OPENWEATHER_API_KEY", "")
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.geo_url = "http://api.openweathermap.org/geo/1.0"
        
        # Cache for reducing API calls
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = 600  # 10 minutes
        
        # Setup handlers
        self._setup_handlers()
        
    def _setup_handlers(self):
        """Setup MCP protocol handlers"""
        
        @self.server.list_resources()
        async def list_resources() -> List[Resource]:
            """List available weather resources"""
            return [
                Resource(
                    uri="weather://current",
                    name="Current Weather",
                    mimeType="application/json",
                    description="Access current weather data for any location"
                ),
                Resource(
                    uri="weather://forecast",
                    name="Weather Forecast",
                    mimeType="application/json",
                    description="Get 5-day weather forecast with 3-hour intervals"
                ),
                Resource(
                    uri="weather://alerts",
                    name="Weather Alerts",
                    mimeType="application/json",
                    description="Get severe weather alerts and warnings"
                ),
                Resource(
                    uri="weather://history",
                    name="Weather History",
                    mimeType="application/json",
                    description="Access historical weather data"
                )
            ]
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read a specific weather resource"""
            if uri == "weather://current":
                return json.dumps({
                    "description": "Current weather resource",
                    "usage": "Use get_current_weather tool with city name or coordinates"
                }, indent=2)
            elif uri == "weather://forecast":
                return json.dumps({
                    "description": "Weather forecast resource",
                    "usage": "Use get_forecast tool with city name or coordinates"
                }, indent=2)
            elif uri == "weather://alerts":
                return json.dumps({
                    "description": "Weather alerts resource",
                    "usage": "Use get_weather_alerts tool with city name or coordinates"
                }, indent=2)
            elif uri == "weather://history":
                return json.dumps({
                    "description": "Historical weather resource",
                    "usage": "Use get_historical_weather tool with city name and date"
                }, indent=2)
            else:
                raise ValueError(f"Unknown resource: {uri}")
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available weather tools"""
            return [
                Tool(
                    name="get_current_weather",
                    description="Get current weather conditions for a specific location",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "City name, state code, and country code (e.g., 'London,UK' or 'New York,NY,US')"
                            },
                            "units": {
                                "type": "string",
                                "enum": ["metric", "imperial", "standard"],
                                "description": "Units of measurement (metric=Celsius, imperial=Fahrenheit, standard=Kelvin)",
                                "default": "metric"
                            }
                        },
                        "required": ["location"]
                    }
                ),
                Tool(
                    name="get_forecast",
                    description="Get 5-day weather forecast with 3-hour intervals",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "City name, state code, and country code"
                            },
                            "units": {
                                "type": "string",
                                "enum": ["metric", "imperial", "standard"],
                                "description": "Units of measurement",
                                "default": "metric"
                            },
                            "days": {
                                "type": "integer",
                                "description": "Number of days to forecast (1-5)",
                                "default": 5,
                                "minimum": 1,
                                "maximum": 5
                            }
                        },
                        "required": ["location"]
                    }
                ),
                Tool(
                    name="search_location",
                    description="Search for a location and get its coordinates",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Location name to search for"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results",
                                "default": 5,
                                "maximum": 10
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="get_weather_by_coordinates",
                    description="Get current weather by latitude and longitude",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "latitude": {
                                "type": "number",
                                "description": "Latitude coordinate"
                            },
                            "longitude": {
                                "type": "number",
                                "description": "Longitude coordinate"
                            },
                            "units": {
                                "type": "string",
                                "enum": ["metric", "imperial", "standard"],
                                "description": "Units of measurement",
                                "default": "metric"
                            }
                        },
                        "required": ["latitude", "longitude"]
                    }
                ),
                Tool(
                    name="get_air_quality",
                    description="Get air quality data for a location",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "latitude": {
                                "type": "number",
                                "description": "Latitude coordinate"
                            },
                            "longitude": {
                                "type": "number",
                                "description": "Longitude coordinate"
                            }
                        },
                        "required": ["latitude", "longitude"]
                    }
                ),
                Tool(
                    name="compare_weather",
                    description="Compare current weather between multiple locations",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "locations": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of city names to compare",
                                "minItems": 2,
                                "maxItems": 5
                            },
                            "units": {
                                "type": "string",
                                "enum": ["metric", "imperial", "standard"],
                                "description": "Units of measurement",
                                "default": "metric"
                            }
                        },
                        "required": ["locations"]
                    }
                ),
                Tool(
                    name="get_weather_alerts",
                    description="Get severe weather alerts for a location",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "City name or location"
                            }
                        },
                        "required": ["location"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> List[TextContent]:
            """Execute a weather tool"""
            try:
                if name == "get_current_weather":
                    result = await self._get_current_weather(arguments)
                elif name == "get_forecast":
                    result = await self._get_forecast(arguments)
                elif name == "search_location":
                    result = await self._search_location(arguments)
                elif name == "get_weather_by_coordinates":
                    result = await self._get_weather_by_coordinates(arguments)
                elif name == "get_air_quality":
                    result = await self._get_air_quality(arguments)
                elif name == "compare_weather":
                    result = await self._compare_weather(arguments)
                elif name == "get_weather_alerts":
                    result = await self._get_weather_alerts(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
                
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "error": str(e),
                        "tool": name,
                        "message": f"Error executing {name}: {str(e)}"
                    }, indent=2)
                )]
    
    def _get_cache_key(self, endpoint: str, params: Dict[str, Any]) -> str:
        """Generate cache key"""
        return f"{endpoint}:{json.dumps(params, sort_keys=True)}"
    
    def _get_cached(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached data if not expired"""
        if key in self.cache:
            cached = self.cache[key]
            if datetime.now().timestamp() - cached["timestamp"] < self.cache_ttl:
                return cached["data"]
            else:
                del self.cache[key]
        return None
    
    def _set_cache(self, key: str, data: Dict[str, Any]):
        """Set cache data"""
        self.cache[key] = {
            "data": data,
            "timestamp": datetime.now().timestamp()
        }
    
    async def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make API request with caching"""
        if not self.api_key:
            return {
                "error": "API key not configured",
                "message": "Please set OPENWEATHER_API_KEY environment variable",
                "signup": "Get free API key at https://openweathermap.org/api"
            }
        
        # Check cache
        cache_key = self._get_cache_key(endpoint, params)
        cached = self._get_cached(cache_key)
        if cached:
            cached["_from_cache"] = True
            return cached
        
        # Make request
        params["appid"] = self.api_key
        
        async with httpx.AsyncClient() as client:
            response = await client.get(endpoint, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            # Cache successful response
            self._set_cache(cache_key, data)
            return data
    
    async def _get_current_weather(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get current weather"""
        location = args.get("location")
        units = args.get("units", "metric")
        
        endpoint = f"{self.base_url}/weather"
        params = {
            "q": location,
            "units": units
        }
        
        data = await self._make_request(endpoint, params)
        
        if "error" in data:
            return data
        
        # Format response
        return {
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
    
    async def _get_forecast(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get weather forecast"""
        location = args.get("location")
        units = args.get("units", "metric")
        days = args.get("days", 5)
        
        endpoint = f"{self.base_url}/forecast"
        params = {
            "q": location,
            "units": units,
            "cnt": days * 8  # 8 intervals per day (3-hour intervals)
        }
        
        data = await self._make_request(endpoint, params)
        
        if "error" in data:
            return data
        
        # Format forecast data
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
    
    async def _search_location(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Search for locations"""
        query = args.get("query")
        limit = args.get("limit", 5)
        
        endpoint = f"{self.geo_url}/direct"
        params = {
            "q": query,
            "limit": limit
        }
        
        data = await self._make_request(endpoint, params)
        
        if "error" in data:
            return data
        
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
            "query": query,
            "results": locations,
            "count": len(locations)
        }
    
    async def _get_weather_by_coordinates(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get weather by coordinates"""
        lat = args.get("latitude")
        lon = args.get("longitude")
        units = args.get("units", "metric")
        
        endpoint = f"{self.base_url}/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "units": units
        }
        
        data = await self._make_request(endpoint, params)
        
        if "error" in data:
            return data
        
        return {
            "location": {
                "name": data.get("name"),
                "country": data.get("sys", {}).get("country"),
                "coordinates": {"latitude": lat, "longitude": lon}
            },
            "current": {
                "temperature": data.get("main", {}).get("temp"),
                "feels_like": data.get("main", {}).get("feels_like"),
                "humidity": data.get("main", {}).get("humidity"),
                "description": data.get("weather", [{}])[0].get("description"),
                "wind_speed": data.get("wind", {}).get("speed")
            },
            "units": units
        }
    
    async def _get_air_quality(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get air quality data"""
        lat = args.get("latitude")
        lon = args.get("longitude")
        
        endpoint = f"{self.base_url}/air_pollution"
        params = {
            "lat": lat,
            "lon": lon
        }
        
        data = await self._make_request(endpoint, params)
        
        if "error" in data:
            return data
        
        aqi_levels = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}
        
        air_data = data.get("list", [{}])[0]
        return {
            "coordinates": {"latitude": lat, "longitude": lon},
            "air_quality_index": air_data.get("main", {}).get("aqi"),
            "aqi_level": aqi_levels.get(air_data.get("main", {}).get("aqi", 0), "Unknown"),
            "components": air_data.get("components", {}),
            "timestamp": datetime.fromtimestamp(air_data.get("dt", 0)).isoformat()
        }
    
    async def _compare_weather(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Compare weather across multiple locations"""
        locations = args.get("locations", [])
        units = args.get("units", "metric")
        
        comparisons = []
        for location in locations:
            try:
                weather = await self._get_current_weather({
                    "location": location,
                    "units": units
                })
                comparisons.append(weather)
            except Exception as e:
                comparisons.append({
                    "location": location,
                    "error": str(e)
                })
        
        return {
            "locations": comparisons,
            "units": units,
            "comparison_time": datetime.now().isoformat()
        }
    
    async def _get_weather_alerts(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get weather alerts (requires One Call API 3.0 - paid tier)"""
        return {
            "message": "Weather alerts require OpenWeatherMap One Call API 3.0 (paid tier)",
            "alternative": "Use get_current_weather to check current conditions",
            "free_tier_note": "Free tier does not include severe weather alerts"
        }
    
    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """Main entry point"""
    server = WeatherMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())

