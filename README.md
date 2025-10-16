# Weather MCP Server

A free, production-ready Model Context Protocol (MCP) server for accessing weather data using the OpenWeatherMap API.

## 🌤️ Overview

This MCP server provides comprehensive weather information through a standardized interface, enabling AI assistants to access real-time weather data, forecasts, air quality information, and more.

## ✨ Features

### 🛠️ Tools (7 Available)

1. **get_current_weather** - Get current weather for any location
2. **get_forecast** - Get 5-day weather forecast with 3-hour intervals
3. **search_location** - Search for locations and get coordinates
4. **get_weather_by_coordinates** - Get weather by latitude/longitude
5. **get_air_quality** - Get air quality index and pollutant data
6. **compare_weather** - Compare weather across multiple cities
7. **get_weather_alerts** - Get severe weather alerts (note: requires paid tier)

### 📚 Resources (4 Available)

- `weather://current` - Current weather data
- `weather://forecast` - Weather forecasts
- `weather://alerts` - Weather alerts and warnings
- `weather://history` - Historical weather data

## 🚀 Quick Start

### Prerequisites

1. **Free API Key** from OpenWeatherMap:
   - Sign up at https://openweathermap.org/api
   - Go to API keys section
   - Copy your API key (free tier includes 1000 calls/day)

2. **Python 3.10+**

### Installation

```bash
cd weather-mcp-server
pip install -e .
```

### Configuration

```bash
# Set your API key
export OPENWEATHER_API_KEY="your_api_key_here"

# Or create a .env file
echo "OPENWEATHER_API_KEY=your_api_key_here" > .env
```

### Run the Server

```bash
python server.py
```

## 💡 Usage Examples

### With Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "weather": {
      "command": "python",
      "args": ["/full/path/to/weather-mcp-server/server.py"],
      "env": {
        "OPENWEATHER_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

Then ask Claude:
- "What's the weather in Paris?"
- "Compare weather between New York, London, and Tokyo"
- "Give me a 5-day forecast for Seattle"
- "What's the air quality in Beijing?"

### With Cursor IDE

Create `.cursor/config.json`:

```json
{
  "mcp": {
    "servers": {
      "weather": {
        "command": "python",
        "args": ["server.py"],
        "cwd": "/full/path/to/weather-mcp-server",
        "env": {
          "OPENWEATHER_API_KEY": "your_api_key_here"
        }
      }
    }
  }
}
```

### Programmatic Usage

```python
from mcp.client import Client
import asyncio

async def main():
    async with Client() as client:
        await client.connect_stdio(
            command="python",
            args=["server.py"],
            env={"OPENWEATHER_API_KEY": "your_key"}
        )
        
        # Get current weather
        result = await client.call_tool(
            "get_current_weather",
            {"location": "London,UK", "units": "metric"}
        )
        print(result)
        
        # Get forecast
        forecast = await client.call_tool(
            "get_forecast",
            {"location": "New York,NY,US", "units": "imperial", "days": 3}
        )
        print(forecast)

asyncio.run(main())
```

## 🔧 Tool Details

### get_current_weather

Get current weather conditions for a location.

**Parameters:**
- `location` (required): City name, e.g., "London,UK", "New York,NY,US"
- `units` (optional): "metric" (Celsius), "imperial" (Fahrenheit), or "standard" (Kelvin)

**Returns:**
```json
{
  "location": {
    "name": "London",
    "country": "GB",
    "coordinates": {"latitude": 51.51, "longitude": -0.13}
  },
  "current": {
    "temperature": 15.5,
    "feels_like": 14.2,
    "humidity": 72,
    "description": "partly cloudy",
    "wind": {"speed": 5.2, "direction": 230},
    "pressure": 1013,
    "visibility": 10000
  },
  "sunrise": "2024-10-16T06:42:00",
  "sunset": "2024-10-16T18:15:00"
}
```

### get_forecast

Get 5-day weather forecast with 3-hour intervals.

**Parameters:**
- `location` (required): City name
- `units` (optional): Temperature units
- `days` (optional): Number of days (1-5, default 5)

**Returns:**
```json
{
  "location": {"name": "Paris", "country": "FR"},
  "forecast": [
    {
      "datetime": "2024-10-16T12:00:00",
      "temperature": 18.5,
      "description": "light rain",
      "humidity": 65,
      "pop": 0.3
    }
  ]
}
```

### search_location

Search for a location and get its coordinates.

**Parameters:**
- `query` (required): Location name to search
- `limit` (optional): Max results (default 5)

**Returns:**
```json
{
  "query": "Springfield",
  "results": [
    {
      "name": "Springfield",
      "country": "US",
      "state": "Illinois",
      "coordinates": {"latitude": 39.78, "longitude": -89.65}
    }
  ]
}
```

### get_weather_by_coordinates

Get weather for specific coordinates.

**Parameters:**
- `latitude` (required): Latitude
- `longitude` (required): Longitude
- `units` (optional): Temperature units

### get_air_quality

Get air quality index and pollutant levels.

**Parameters:**
- `latitude` (required): Latitude
- `longitude` (required): Longitude

**Returns:**
```json
{
  "air_quality_index": 2,
  "aqi_level": "Fair",
  "components": {
    "co": 201.94,
    "no2": 13.56,
    "o3": 68.66,
    "pm2_5": 5.28,
    "pm10": 7.32
  }
}
```

### compare_weather

Compare current weather across multiple cities.

**Parameters:**
- `locations` (required): Array of city names (2-5 cities)
- `units` (optional): Temperature units

**Returns:**
Comparison of weather data for all locations.

## 📊 API Limits

### Free Tier (OpenWeatherMap)
- **Calls per day:** 1,000
- **Calls per minute:** 60
- **Features included:**
  - Current weather
  - 5-day forecast
  - Geocoding
  - Air pollution data

### Caching
The server automatically caches responses for 10 minutes to reduce API calls.

## 🌍 Supported Units

- **metric**: Temperature in Celsius, wind speed in m/s
- **imperial**: Temperature in Fahrenheit, wind speed in mph
- **standard**: Temperature in Kelvin, wind speed in m/s

## 🔐 Security

- API key stored in environment variable (never in code)
- HTTPS-only communication with OpenWeatherMap
- Input validation for all parameters
- Rate limiting awareness

## 🐛 Troubleshooting

### "API key not configured" error

```bash
# Make sure you set the environment variable
export OPENWEATHER_API_KEY="your_key"

# Or check if it's set
echo $OPENWEATHER_API_KEY
```

### "401 Unauthorized" error

- Verify your API key is correct
- Check if API key is activated (can take a few hours after signup)
- Ensure you're using the free tier correctly

### Rate limit errors

The free tier allows 60 calls/minute and 1000/day. The server caches responses for 10 minutes to help avoid limits.

## 📚 Resources

- **OpenWeatherMap API Docs:** https://openweathermap.org/api
- **Free API Signup:** https://openweathermap.org/price
- **MCP Specification:** https://modelcontextprotocol.io
- **OpenWeatherMap Weather Codes:** https://openweathermap.org/weather-conditions

## 🧪 Testing

```bash
# Run tests
pytest tests/ -v

# Test specific tool
python -c "
import asyncio
from server import WeatherMCPServer

async def test():
    server = WeatherMCPServer()
    result = await server._get_current_weather({
        'location': 'London,UK',
        'units': 'metric'
    })
    print(result)

asyncio.run(test())
"
```

## 🎯 Example Queries

Ask your AI assistant:

1. **Current Weather:**
   - "What's the weather like in Tokyo?"
   - "Is it raining in Seattle right now?"
   - "What's the temperature in Miami?"

2. **Forecasts:**
   - "Give me a 3-day forecast for Paris"
   - "Will it rain in London this week?"
   - "What's the weather going to be like tomorrow in NYC?"

3. **Comparisons:**
   - "Compare the weather in Sydney, London, and New York"
   - "Which is warmer: Dubai or Bangkok?"

4. **Air Quality:**
   - "What's the air quality in Delhi?"
   - "Is the air quality good in Los Angeles?"

5. **Location Search:**
   - "Find all cities named Portland"
   - "Search for Springfield locations"

## 💻 Development

### Project Structure
```
weather-mcp-server/
├── server.py           # Main server implementation
├── README.md          # This file
├── requirements.txt   # Python dependencies
├── pyproject.toml    # Package configuration
└── tests/            # Test suite
    └── test_server.py
```

### Adding Custom Tools

```python
# In server.py, add to list_tools():
Tool(
    name="your_custom_tool",
    description="Description",
    inputSchema={...}
)

# Add handler method:
async def _your_custom_tool(self, args):
    # Implementation
    pass

# Add to call_tool():
elif name == "your_custom_tool":
    result = await self._your_custom_tool(arguments)
```

## 📄 License

MIT License - Free to use, modify, and distribute

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests
4. Submit a pull request

## ⭐ Features Coming Soon

- Historical weather data
- Weather maps
- UV index information
- Marine weather data
- Agricultural weather data

## 📞 Support

- **Issues:** GitHub Issues
- **OpenWeatherMap Support:** https://openweathermap.org/faq
- **MCP Community:** https://modelcontextprotocol.io

---

**Built with ❤️ using OpenWeatherMap Free API**

*Get started in 5 minutes with free weather data for your AI!*

