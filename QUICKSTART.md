# Weather MCP Server - Quick Start 🚀

Get weather data in your AI assistant in just 3 minutes!

## Step 1: Get Free API Key (2 minutes)

1. Go to https://openweathermap.org/api
2. Click "Sign Up" (it's FREE!)
3. Verify your email
4. Go to "API keys" section
5. Copy your API key

**Note:** Free tier gives you 1,000 API calls per day - perfect for personal use!

## Step 2: Install (30 seconds)

```bash
cd weather-mcp-server
pip install -e .
```

## Step 3: Configure (30 seconds)

```bash
# Set your API key
export OPENWEATHER_API_KEY="your_api_key_from_step_1"
```

Or create a `.env` file:
```bash
echo "OPENWEATHER_API_KEY=your_api_key_here" > .env
```

## Step 4: Test It! (30 seconds)

```bash
python server.py
```

You should see the server start without errors! ✅

## Using with Claude Desktop

1. **Edit Claude config:**
   ```bash
   # macOS
   open ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

2. **Add this configuration:**
   ```json
   {
     "mcpServers": {
       "weather": {
         "command": "python",
         "args": ["/full/path/to/weather-mcp-server/server.py"],
         "env": {
           "OPENWEATHER_API_KEY": "your_api_key"
         }
       }
     }
   }
   ```

3. **Restart Claude Desktop**

4. **Try it out!** Ask Claude:
   - "What's the weather in Paris?"
   - "Give me a 5-day forecast for Tokyo"
   - "Compare weather in NYC, London, and Sydney"

## Example Queries

### Current Weather
```
You: "What's the weather in London?"

Claude: [Uses get_current_weather]
"The current weather in London, UK is partly cloudy with a temperature 
of 15°C (feels like 14°C). Humidity is at 72% with light winds from 
the southwest at 5.2 m/s. Sunrise was at 6:42 AM and sunset will be 
at 6:15 PM."
```

### Weather Forecast
```
You: "Will it rain in Seattle this week?"

Claude: [Uses get_forecast]
"Looking at the 5-day forecast for Seattle, WA:
- Today: Cloudy, 16°C, 30% chance of rain
- Tomorrow: Light rain, 14°C, 60% chance of rain
- Friday: Partly cloudy, 15°C, 20% chance of rain
..."
```

### Compare Cities
```
You: "Which is warmer: Dubai or Miami?"

Claude: [Uses compare_weather]
"Dubai is currently warmer at 35°C (95°F) compared to Miami at 28°C (82°F).
Dubai also has lower humidity at 45% vs Miami's 78%."
```

### Air Quality
```
You: "What's the air quality in Beijing?"

Claude: [Uses search_location + get_air_quality]
"The air quality in Beijing is currently rated as 'Moderate' with an 
AQI of 3. PM2.5 levels are at 25 μg/m³ and PM10 at 45 μg/m³."
```

## Available Tools

Once connected, Claude/Cursor will have access to:

- ✅ **get_current_weather** - Current conditions
- ✅ **get_forecast** - 5-day forecast
- ✅ **search_location** - Find cities
- ✅ **get_weather_by_coordinates** - Weather by lat/lon
- ✅ **get_air_quality** - Air quality index
- ✅ **compare_weather** - Compare multiple cities
- ✅ **get_weather_alerts** - Severe weather alerts

## Troubleshooting

### "API key not configured"
```bash
# Make sure environment variable is set
echo $OPENWEATHER_API_KEY

# If empty, set it again
export OPENWEATHER_API_KEY="your_key"
```

### "401 Unauthorized"
- Your API key might not be activated yet (wait a few hours after signup)
- Check if you copied the key correctly
- Make sure you're using the correct API key format

### Tools not showing in Claude
1. Check the config file path is absolute
2. Restart Claude Desktop completely
3. Check Claude logs: `~/Library/Logs/Claude/`

### Rate limit reached
Free tier allows 60 calls/minute. The server caches responses for 10 minutes to help avoid this.

## What's Next?

- Read the full [README.md](./README.md)
- Check example queries below
- Customize the caching behavior
- Add your own weather tools

## More Examples

### Planning Activities
```
"Should I go hiking in Yosemite this weekend? Check the forecast."
"Is it a good day for a beach trip in San Diego?"
"What's the weather like for the football game in Chicago tonight?"
```

### Travel Planning
```
"What's the weather forecast for my trip to Barcelona next week?"
"Compare weather in Bali, Phuket, and Maldives for December"
"What should I pack for Paris in October?"
```

### Daily Questions
```
"Do I need an umbrella today in Boston?"
"What's the temperature difference between day and night in Phoenix?"
"Is it going to be windy for my morning run?"
```

## Tips

1. **Be specific with location names** - Include country code for best results:
   - ✅ "London,UK"
   - ✅ "Paris,FR"
   - ❌ "London" (might give you London, Ontario instead!)

2. **Specify units** - Tell Claude what units you prefer:
   - "in Celsius"
   - "in Fahrenheit"
   - Or set default in the tool call

3. **Use natural language** - Claude will automatically use the right tools:
   - "What's it like in Tokyo?" → uses get_current_weather
   - "How's the weather this week?" → uses get_forecast
   - "Where's Springfield?" → uses search_location

## Free API Limits

| Feature | Free Tier |
|---------|-----------|
| Calls per day | 1,000 |
| Calls per minute | 60 |
| Current weather | ✅ Yes |
| 5-day forecast | ✅ Yes |
| Air quality | ✅ Yes |
| Historical data | ❌ No (paid) |

## Success! 🎉

You're all set! Your AI assistant now has access to weather data from anywhere in the world.

Ask Claude or Cursor about the weather and watch it work! ☀️🌧️❄️

---

**Need help?** Check the [README.md](./README.md) or [OpenWeatherMap Docs](https://openweathermap.org/api)

