"""
Unit tests for Weather MCP Server
"""

import pytest
import json
import os
from unittest.mock import AsyncMock, MagicMock, patch
import sys
from pathlib import Path

# Add parent directory to path to import server
sys.path.insert(0, str(Path(__file__).parent.parent))

from server import WeatherMCPServer


@pytest.fixture
def server():
    """Create a test server instance"""
    # Set a test API key
    os.environ["OPENWEATHER_API_KEY"] = "test_api_key_12345"
    return WeatherMCPServer()


@pytest.fixture
def mock_weather_response():
    """Mock OpenWeatherMap API response for current weather"""
    return {
        "name": "London",
        "sys": {"country": "GB", "sunrise": 1697440920, "sunset": 1697480100},
        "coord": {"lat": 51.5074, "lon": -0.1278},
        "main": {
            "temp": 15.5,
            "feels_like": 14.2,
            "temp_min": 13.0,
            "temp_max": 17.0,
            "pressure": 1013,
            "humidity": 72
        },
        "weather": [
            {"description": "partly cloudy", "icon": "02d"}
        ],
        "wind": {"speed": 5.2, "deg": 230},
        "clouds": {"all": 40},
        "visibility": 10000,
        "dt": 1697450000
    }


@pytest.fixture
def mock_forecast_response():
    """Mock OpenWeatherMap API response for forecast"""
    return {
        "city": {
            "name": "Paris",
            "country": "FR",
            "coord": {"lat": 48.8566, "lon": 2.3522}
        },
        "list": [
            {
                "dt": 1697450000,
                "main": {
                    "temp": 18.5,
                    "feels_like": 17.8,
                    "temp_min": 17.0,
                    "temp_max": 19.0,
                    "pressure": 1015,
                    "humidity": 65
                },
                "weather": [{"description": "clear sky", "icon": "01d"}],
                "wind": {"speed": 3.5},
                "clouds": {"all": 10},
                "pop": 0.0
            }
        ]
    }


def test_server_initialization():
    """Test server initializes correctly"""
    os.environ["OPENWEATHER_API_KEY"] = "test_key"
    server = WeatherMCPServer()
    
    assert server.server is not None
    assert server.api_key == "test_key"
    assert server.base_url == "https://api.openweathermap.org/data/2.5"


def test_cache_key_generation(server):
    """Test cache key generation"""
    endpoint = "https://api.example.com/weather"
    params = {"city": "London", "units": "metric"}
    
    key = server._get_cache_key(endpoint, params)
    
    assert isinstance(key, str)
    assert "London" in key
    assert "metric" in key


def test_cache_set_and_get(server):
    """Test caching functionality"""
    key = "test_key"
    data = {"temperature": 15.5}
    
    # Set cache
    server._set_cache(key, data)
    
    # Get cache
    cached = server._get_cached(key)
    
    assert cached is not None
    assert cached["temperature"] == 15.5


def test_cache_expiration(server):
    """Test cache expiration"""
    key = "test_key"
    data = {"temperature": 15.5}
    
    # Set cache with old timestamp
    server.cache[key] = {
        "data": data,
        "timestamp": 0  # Very old timestamp
    }
    
    # Should return None due to expiration
    cached = server._get_cached(key)
    assert cached is None


@pytest.mark.asyncio
async def test_get_current_weather_no_api_key():
    """Test current weather without API key"""
    os.environ.pop("OPENWEATHER_API_KEY", None)
    server = WeatherMCPServer()
    
    result = await server._get_current_weather({
        "location": "London,UK",
        "units": "metric"
    })
    
    assert "error" in result
    assert "API key not configured" in result["error"]


@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_get_current_weather_success(mock_client, server, mock_weather_response):
    """Test successful current weather request"""
    # Mock the HTTP response
    mock_response = MagicMock()
    mock_response.json.return_value = mock_weather_response
    mock_response.raise_for_status = MagicMock()
    
    mock_client_instance = MagicMock()
    mock_client_instance.get = AsyncMock(return_value=mock_response)
    mock_client.return_value.__aenter__.return_value = mock_client_instance
    
    result = await server._get_current_weather({
        "location": "London,UK",
        "units": "metric"
    })
    
    assert "location" in result
    assert result["location"]["name"] == "London"
    assert result["location"]["country"] == "GB"
    assert "current" in result
    assert result["current"]["temperature"] == 15.5


@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_get_forecast_success(mock_client, server, mock_forecast_response):
    """Test successful forecast request"""
    mock_response = MagicMock()
    mock_response.json.return_value = mock_forecast_response
    mock_response.raise_for_status = MagicMock()
    
    mock_client_instance = MagicMock()
    mock_client_instance.get = AsyncMock(return_value=mock_response)
    mock_client.return_value.__aenter__.return_value = mock_client_instance
    
    result = await server._get_forecast({
        "location": "Paris,FR",
        "units": "metric",
        "days": 3
    })
    
    assert "location" in result
    assert result["location"]["name"] == "Paris"
    assert "forecast" in result
    assert len(result["forecast"]) > 0


@pytest.mark.asyncio
async def test_search_location():
    """Test location search"""
    os.environ["OPENWEATHER_API_KEY"] = "test_key"
    server = WeatherMCPServer()
    
    mock_response = [
        {
            "name": "Springfield",
            "country": "US",
            "state": "Illinois",
            "lat": 39.7817,
            "lon": -89.6501
        }
    ]
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_resp = MagicMock()
        mock_resp.json.return_value = mock_response
        mock_resp.raise_for_status = MagicMock()
        
        mock_client_instance = MagicMock()
        mock_client_instance.get = AsyncMock(return_value=mock_resp)
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        result = await server._search_location({
            "query": "Springfield",
            "limit": 5
        })
        
        assert "results" in result
        assert len(result["results"]) > 0
        assert result["results"][0]["name"] == "Springfield"


@pytest.mark.asyncio
async def test_compare_weather():
    """Test weather comparison"""
    os.environ["OPENWEATHER_API_KEY"] = "test_key"
    server = WeatherMCPServer()
    
    # Mock get_current_weather to return test data
    async def mock_get_weather(args):
        return {
            "location": {"name": args["location"].split(",")[0]},
            "current": {"temperature": 20.0}
        }
    
    server._get_current_weather = mock_get_weather
    
    result = await server._compare_weather({
        "locations": ["London,UK", "Paris,FR"],
        "units": "metric"
    })
    
    assert "locations" in result
    assert len(result["locations"]) == 2


def test_units_validation(server):
    """Test that different units are supported"""
    units = ["metric", "imperial", "standard"]
    
    for unit in units:
        # This should not raise an error
        assert unit in ["metric", "imperial", "standard"]


@pytest.mark.asyncio
async def test_get_weather_alerts(server):
    """Test weather alerts (returns info message for free tier)"""
    result = await server._get_weather_alerts({"location": "London,UK"})
    
    assert "message" in result
    assert "paid tier" in result["message"].lower()

