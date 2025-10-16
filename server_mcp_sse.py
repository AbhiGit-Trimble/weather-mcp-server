#!/usr/bin/env python3
"""
Weather MCP Server - Official MCP Protocol with SSE
A proper Model Context Protocol server using official SDK
"""

import os
import json
from typing import Any, Dict, Optional
from datetime import datetime
import httpx
import uvicorn
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent
import mcp.types as types


class WeatherMCPServer:
    """MCP Server for Weather Data using official protocol"""

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

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
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
                                "description": "City name (e.g., 'London,UK')"
                            },
                            "units": {
                                "type": "string",
                                "enum": ["metric", "imperial", "standard"],
                                "default": "metric"
                            }
                        },
                        "required": ["location"]
                    }
                ),
                Tool(
                    name="get_forecast",
                    description="Get 5-day weather forecast",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "City name"
                            },
                            "units": {
                                "type": "string",
                                "enum": ["metric", "imperial", "standard"],
                                "default": "metric"
                            },
                            "days": {
                                "type": "integer",
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
                    description="Search for a location and get coordinates",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Location name"
                            },
                            "limit": {
                                "type": "integer",
                                "default": 5
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="get_weather_by_coordinates",
                    description="Get weather by GPS coordinates",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "latitude": {"type": "number"},
                            "longitude": {"type": "number"},
                            "units": {
                                "type": "string",
                                "enum": ["metric", "imperial", "standard"],
                                "default": "metric"
                            }
                        },
                        "required": ["latitude", "longitude"]
                    }
                ),
                Tool(
                    name="get_air_quality",
                    description="Get air quality data for coordinates",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "latitude": {"type": "number"},
                            "longitude": {"type": "number"}
                        },
                        "required": ["latitude", "longitude"]
                    }
                ),
                Tool(
                    name="compare_weather",
                    description="Compare weather across multiple locations",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "locations": {
                                "type": "array",
                                "items": {"type": "string"},
                                "minItems": 2,
                                "maxItems": 5
                            },
                            "units": {
                                "type": "string",
                                "default": "metric"
                            }
                        },
                        "required": ["locations"]
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
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
                        "tool": name
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
                "message": "Please set OPENWEATHER_API_KEY environment variable"
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
        params = {"q": location, "units": units}

        data = await self._make_request(endpoint, params)

        if "error" in data:
            return data

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
                "humidity": data.get("main", {}).get("humidity"),
                "description": data.get("weather", [{}])[0].get("description"),
                "wind_speed": data.get("wind", {}).get("speed")
            },
            "units": units
        }

    async def _get_forecast(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get weather forecast"""
        location = args.get("location")
        units = args.get("units", "metric")
        days = args.get("days", 5)

        endpoint = f"{self.base_url}/forecast"
        params = {"q": location, "units": units, "cnt": days * 8}

        data = await self._make_request(endpoint, params)

        if "error" in data:
            return data

        forecasts = []
        for item in data.get("list", []):
            forecasts.append({
                "datetime": datetime.fromtimestamp(item.get("dt", 0)).isoformat(),
                "temperature": item.get("main", {}).get("temp"),
                "description": item.get("weather", [{}])[0].get("description"),
                "humidity": item.get("main", {}).get("humidity")
            })

        return {
            "location": {
                "name": data.get("city", {}).get("name"),
                "country": data.get("city", {}).get("country")
            },
            "forecast": forecasts,
            "units": units
        }

    async def _search_location(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Search for locations"""
        query = args.get("query")
        limit = args.get("limit", 5)

        endpoint = f"{self.geo_url}/direct"
        params = {"q": query, "limit": limit}

        data = await self._make_request(endpoint, params)

        if "error" in data:
            return data

        locations = []
        for item in data:
            locations.append({
                "name": item.get("name"),
                "country": item.get("country"),
                "state": item.get("state"),
                "coordinates": {
                    "latitude": item.get("lat"),
                    "longitude": item.get("lon")
                }
            })

        return {"query": query, "results": locations}

    async def _get_weather_by_coordinates(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get weather by coordinates"""
        lat = args.get("latitude")
        lon = args.get("longitude")
        units = args.get("units", "metric")

        endpoint = f"{self.base_url}/weather"
        params = {"lat": lat, "lon": lon, "units": units}

        data = await self._make_request(endpoint, params)

        if "error" in data:
            return data

        return {
            "location": {
                "name": data.get("name"),
                "coordinates": {"latitude": lat, "longitude": lon}
            },
            "current": {
                "temperature": data.get("main", {}).get("temp"),
                "description": data.get("weather", [{}])[0].get("description"),
                "humidity": data.get("main", {}).get("humidity")
            },
            "units": units
        }

    async def _get_air_quality(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get air quality data"""
        lat = args.get("latitude")
        lon = args.get("longitude")

        endpoint = f"{self.base_url}/air_pollution"
        params = {"lat": lat, "lon": lon}

        data = await self._make_request(endpoint, params)

        if "error" in data:
            return data

        aqi_levels = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}
        air_data = data.get("list", [{}])[0]

        return {
            "coordinates": {"latitude": lat, "longitude": lon},
            "air_quality_index": air_data.get("main", {}).get("aqi"),
            "aqi_level": aqi_levels.get(air_data.get("main", {}).get("aqi", 0), "Unknown"),
            "components": air_data.get("components", {})
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
                comparisons.append({"location": location, "error": str(e)})

        return {"locations": comparisons, "units": units}

    def get_sse_app(self):
        """Get SSE-enabled ASGI app"""
        from starlette.applications import Starlette
        from starlette.routing import Route, Mount
        from starlette.responses import Response, JSONResponse

        # Create SSE transport
        transport = SseServerTransport("/messages")

        async def handle_sse(request):
            """Handle SSE connection"""
            async with transport.connect_sse(
                request.scope,
                request.receive,
                request._send
            ) as streams:
                await self.server.run(
                    streams[0],
                    streams[1],
                    self.server.create_initialization_options()
                )
            return Response()

        async def health(request):
            """Health check"""
            return JSONResponse({
                "status": "healthy",
                "api_key_configured": bool(self.api_key),
                "protocol": "MCP SSE/Streamable HTTP"
            })

        app = Starlette(
            routes=[
                Route("/sse", endpoint=handle_sse),
                Mount("/messages", app=transport.handle_post_message),
                Route("/health", endpoint=health),
            ]
        )

        return app


def main():
    """Run the MCP server with SSE"""
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")

    print(f"🌤️  Weather MCP Server (SSE/Streamable HTTP)")
    print(f"📍 Running on: http://{host}:{port}")
    print(f"🔑 API Key configured: {bool(os.getenv('OPENWEATHER_API_KEY'))}")
    print(f"📡 SSE endpoint: /sse")
    print(f"✉️  Messages endpoint: /messages")
    print(f"✨ Ready to serve weather data!")

    server = WeatherMCPServer()
    app = server.get_sse_app()

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
