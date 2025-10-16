#!/usr/bin/env python3
"""
Weather MCP Server - HTTP Version
A Model Context Protocol server for weather data via HTTP/REST API
"""

import os
import json
from typing import Any, Dict, List, Optional
from datetime import datetime
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn


# Pydantic models for request/response
class ToolCallRequest(BaseModel):
    tool: str
    arguments: Dict[str, Any]


class ResourceRequest(BaseModel):
    uri: str


class WeatherHTTPServer:
    """HTTP-based Weather MCP Server"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY", "")
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.geo_url = "http://api.openweathermap.org/geo/1.0"
        
        # Cache for reducing API calls
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = int(os.getenv("CACHE_TTL", "600"))  # 10 minutes
        
        # Create FastAPI app
        self.app = FastAPI(
            title="Weather MCP Server",
            description="Model Context Protocol server for weather data",
            version="1.0.0"
        )
        
        # Add CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Setup routes
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/")
        async def root():
            """Root endpoint"""
            return {
                "name": "Weather MCP Server",
                "version": "1.0.0",
                "protocol": "MCP over HTTP",
                "status": "running"
            }
        
        @self.app.get("/mcp")
        async def mcp_info():
            """MCP base endpoint"""
            return {
                "protocol": "MCP",
                "version": "1.0.0",
                "capabilities": {
                    "tools": True,
                    "resources": True
                },
                "endpoints": {
                    "tools": "/mcp/tools",
                    "call_tool": "/mcp/tools/call",
                    "resources": "/mcp/resources",
                    "read_resource": "/mcp/resources/read"
                }
            }
        
        @self.app.get("/health")
        async def health():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "api_key_configured": bool(self.api_key),
                "cache_size": len(self.cache)
            }
        
        @self.app.get("/mcp/resources")
        async def list_resources():
            """List available resources"""
            return {
                "resources": [
                    {
                        "uri": "weather://current",
                        "name": "Current Weather",
                        "mimeType": "application/json",
                        "description": "Access current weather data for any location"
                    },
                    {
                        "uri": "weather://forecast",
                        "name": "Weather Forecast",
                        "mimeType": "application/json",
                        "description": "Get 5-day weather forecast"
                    },
                    {
                        "uri": "weather://alerts",
                        "name": "Weather Alerts",
                        "mimeType": "application/json",
                        "description": "Get weather alerts"
                    }
                ]
            }
        
        @self.app.post("/mcp/resources/read")
        async def read_resource(request: ResourceRequest):
            """Read a specific resource"""
            uri = request.uri
            
            if uri == "weather://current":
                return {
                    "description": "Current weather resource",
                    "usage": "Use get_current_weather tool"
                }
            elif uri == "weather://forecast":
                return {
                    "description": "Weather forecast resource",
                    "usage": "Use get_forecast tool"
                }
            else:
                raise HTTPException(status_code=404, detail=f"Resource not found: {uri}")
        
        @self.app.get("/mcp/tools")
        async def list_tools():
            """List available tools"""
            return {
                "tools": [
                    {
                        "name": "get_current_weather",
                        "description": "Get current weather conditions for a specific location",
                        "inputSchema": {
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
                    },
                    {
                        "name": "get_forecast",
                        "description": "Get 5-day weather forecast",
                        "inputSchema": {
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
                    },
                    {
                        "name": "search_location",
                        "description": "Search for a location",
                        "inputSchema": {
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
                    },
                    {
                        "name": "get_weather_by_coordinates",
                        "description": "Get weather by coordinates",
                        "inputSchema": {
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
                    },
                    {
                        "name": "get_air_quality",
                        "description": "Get air quality data",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "latitude": {"type": "number"},
                                "longitude": {"type": "number"}
                            },
                            "required": ["latitude", "longitude"]
                        }
                    },
                    {
                        "name": "compare_weather",
                        "description": "Compare weather across locations",
                        "inputSchema": {
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
                    }
                ]
            }
        
        @self.app.post("/mcp/tools/call")
        async def call_tool(request: ToolCallRequest):
            """Execute a tool"""
            try:
                tool = request.tool
                args = request.arguments
                
                if tool == "get_current_weather":
                    result = await self._get_current_weather(args)
                elif tool == "get_forecast":
                    result = await self._get_forecast(args)
                elif tool == "search_location":
                    result = await self._search_location(args)
                elif tool == "get_weather_by_coordinates":
                    result = await self._get_weather_by_coordinates(args)
                elif tool == "get_air_quality":
                    result = await self._get_air_quality(args)
                elif tool == "compare_weather":
                    result = await self._compare_weather(args)
                else:
                    raise HTTPException(status_code=400, detail=f"Unknown tool: {tool}")
                
                return {"result": result}
                
            except Exception as e:
                return {
                    "error": str(e),
                    "tool": request.tool
                }
    
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
                "wind_speed": data.get("wind", {}).get("speed"),
                "pressure": data.get("main", {}).get("pressure"),
                "clouds": data.get("clouds", {}).get("all")
            },
            "timestamp": datetime.fromtimestamp(data.get("dt", 0)).isoformat(),
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
                "humidity": item.get("main", {}).get("humidity"),
                "wind_speed": item.get("wind", {}).get("speed"),
                "pop": item.get("pop", 0)
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


# Create server instance
weather_server = WeatherHTTPServer()
app = weather_server.app


def main():
    """Run the HTTP server"""
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"🌤️  Weather MCP Server (HTTP)")
    print(f"📍 Running on: http://{host}:{port}")
    print(f"🔑 API Key configured: {bool(weather_server.api_key)}")
    print(f"📚 MCP Endpoints:")
    print(f"   - GET  /mcp/tools")
    print(f"   - POST /mcp/tools/call")
    print(f"   - GET  /mcp/resources")
    print(f"   - POST /mcp/resources/read")
    print(f"✨ Ready to serve weather data!")
    
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()

