"""
Common utilities and constants for the weather MCP server tools.
"""

import os
import json
from typing import Dict, Any, Optional
from datetime import datetime
import httpx

# Constants
BASE_URL = "https://api.openweathermap.org/data/2.5"
GEO_URL = "http://api.openweathermap.org/geo/1.0"
API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

# Cache
_cache: Dict[str, Dict[str, Any]] = {}
CACHE_TTL = 600  # 10 minutes


def get_cache_key(endpoint: str, params: Dict[str, Any]) -> str:
    """Generate cache key."""
    return f"{endpoint}:{json.dumps(params, sort_keys=True)}"


def get_cached(key: str) -> Optional[Dict[str, Any]]:
    """Get cached data if not expired."""
    if key in _cache:
        cached = _cache[key]
        if datetime.now().timestamp() - cached["timestamp"] < CACHE_TTL:
            return cached["data"]
        else:
            del _cache[key]
    return None


def set_cache(key: str, data: Dict[str, Any]):
    """Set cache data."""
    _cache[key] = {
        "data": data,
        "timestamp": datetime.now().timestamp()
    }


async def make_weather_request(endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Make API request to OpenWeatherMap with caching.

    Args:
        endpoint: API endpoint URL
        params: Query parameters

    Returns:
        Dictionary with success status and data or error information
    """
    if not API_KEY:
        return {
            "success": False,
            "error": "API key not configured. Please set OPENWEATHER_API_KEY environment variable."
        }

    # Check cache
    cache_key = get_cache_key(endpoint, params)
    cached = get_cached(cache_key)
    if cached:
        cached["_from_cache"] = True
        return {"success": True, "data": cached}

    # Make request
    params["appid"] = API_KEY

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(endpoint, params=params, timeout=10.0)

            if response.status_code == 200:
                data = response.json()
                set_cache(cache_key, data)
                return {"success": True, "data": data}
            elif response.status_code == 401:
                return {
                    "success": False,
                    "error": "Invalid API key",
                    "status_code": 401
                }
            elif response.status_code == 404:
                return {
                    "success": False,
                    "error": "Location not found",
                    "status_code": 404
                }
            else:
                return {
                    "success": False,
                    "error": f"API error: {response.status_code}",
                    "status_code": response.status_code
                }

    except httpx.TimeoutException:
        return {
            "success": False,
            "error": "Request timed out"
        }
    except httpx.RequestError as e:
        return {
            "success": False,
            "error": f"Request failed: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }


def handle_request_exceptions(response_func, *args, **kwargs):
    """Handle common request exceptions for API calls."""
    try:
        return response_func(*args, **kwargs)
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }
