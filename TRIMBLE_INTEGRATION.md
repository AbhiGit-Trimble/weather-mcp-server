# Using Weather MCP with Trimble Agentic Platform

This guide shows how to integrate the Weather MCP Server with the Trimble Agentic Platform.

## Overview

The Trimble Agentic Platform supports MCP (Model Context Protocol) servers as tools for agents. This allows your Trimble AI agents to access real-time weather data from anywhere in the world.

## Prerequisites

1. **Trimble AI Platform Access** - Account and API key
2. **OpenWeatherMap API Key** - Free at https://openweathermap.org/api
3. **Weather MCP Server** - Already installed in this directory

## Quick Setup

### Step 1: Configure the MCP Server for Trimble

Create a configuration file for Trimble: `trimble-weather-config.json`

```json
{
  "mcp_server": {
    "name": "weather-mcp",
    "description": "Real-time weather data and forecasts",
    "command": "python",
    "args": ["/Users/abhalek/Documents/Agentic Platform/MCPs/weather-mcp-server/server.py"],
    "env": {
      "OPENWEATHER_API_KEY": "your_openweather_api_key_here"
    }
  },
  "capabilities": {
    "tools": [
      "get_current_weather",
      "get_forecast",
      "search_location",
      "get_weather_by_coordinates",
      "get_air_quality",
      "compare_weather",
      "get_weather_alerts"
    ],
    "resources": [
      "weather://current",
      "weather://forecast",
      "weather://alerts",
      "weather://history"
    ]
  }
}
```

### Step 2: Create or Update a Trimble Agent

#### Option A: Using Trimble Web Interface

1. Go to https://agents.trimble-ai.com
2. Create a new agent or edit existing one
3. Navigate to "Tools & Integrations"
4. Click "Add MCP Server"
5. Upload or paste the configuration above
6. Save the agent

#### Option B: Using Trimble API

```bash
# Create agent with Weather MCP configured
curl -X POST https://agents.trimble-ai.com/v1/agents \
  -H "Authorization: Bearer YOUR_TRIMBLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Weather-Enabled Assistant",
    "description": "AI assistant with access to real-time weather data",
    "model": "gpt-4",
    "mcp_servers": {
      "weather": {
        "command": "python",
        "args": ["/Users/abhalek/Documents/Agentic Platform/MCPs/weather-mcp-server/server.py"],
        "env": {
          "OPENWEATHER_API_KEY": "your_openweather_key"
        }
      }
    }
  }'
```

#### Option C: Using Python SDK

```python
import requests

TRIMBLE_API_KEY = "your_trimble_api_key"
OPENWEATHER_API_KEY = "your_openweather_key"

# Create agent with weather capabilities
response = requests.post(
    "https://agents.trimble-ai.com/v1/agents",
    headers={
        "Authorization": f"Bearer {TRIMBLE_API_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "name": "Weather Assistant",
        "description": "AI assistant with weather data access",
        "model": "gpt-4",
        "instructions": "You have access to weather data. Use it to answer weather-related questions accurately.",
        "mcp_servers": {
            "weather": {
                "command": "python",
                "args": ["/Users/abhalek/Documents/Agentic Platform/MCPs/weather-mcp-server/server.py"],
                "env": {
                    "OPENWEATHER_API_KEY": OPENWEATHER_API_KEY
                }
            }
        }
    }
)

agent = response.json()
print(f"Created agent: {agent['id']}")
```

### Step 3: Test the Integration

Execute the agent with a weather query:

```bash
curl -X POST https://agents.trimble-ai.com/v1/agents/AGENT_ID/runs \
  -H "Authorization: Bearer YOUR_TRIMBLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "What is the weather in Paris right now?"
  }'
```

## Configuration Options

### Environment Variables

```json
{
  "env": {
    "OPENWEATHER_API_KEY": "required_api_key",
    "CACHE_TTL": "600",
    "LOG_LEVEL": "INFO"
  }
}
```

### Tool Permissions

Specify which weather tools the agent can use:

```json
{
  "mcp_servers": {
    "weather": {
      "command": "python",
      "args": ["server.py"],
      "enabled_tools": [
        "get_current_weather",
        "get_forecast",
        "compare_weather"
      ]
    }
  }
}
```

## Example Use Cases

### Construction Planning Agent

```json
{
  "name": "Construction Weather Advisor",
  "description": "Monitors weather for construction site planning",
  "instructions": "Monitor weather conditions for construction sites. Alert about adverse weather that could impact work schedules. Provide 5-day forecasts for project planning.",
  "mcp_servers": {
    "weather": {
      "command": "python",
      "args": ["/full/path/to/server.py"],
      "env": {"OPENWEATHER_API_KEY": "key"}
    }
  }
}
```

**Example queries:**
- "Check weather at our Seattle construction site"
- "Will rain delay our concrete pour scheduled for tomorrow?"
- "Compare weather conditions at all our active project sites"

### Field Service Assistant

```json
{
  "name": "Field Service Weather Assistant",
  "description": "Helps field technicians plan service visits based on weather",
  "instructions": "Provide weather forecasts for field service locations. Help technicians plan their routes considering weather conditions.",
  "mcp_servers": {
    "weather": {
      "command": "python",
      "args": ["/full/path/to/server.py"],
      "env": {"OPENWEATHER_API_KEY": "key"}
    }
  }
}
```

**Example queries:**
- "What's the weather for my site visits today?"
- "Should I reschedule the outdoor equipment installation?"
- "Check weather along my route from Denver to Boulder"

### Project Management Agent

```json
{
  "name": "Project Weather Tracker",
  "description": "Tracks weather impact on project timelines",
  "instructions": "Monitor weather conditions that could affect project schedules. Provide early warnings for adverse weather. Track weather patterns for project reporting.",
  "mcp_servers": {
    "weather": {
      "command": "python",
      "args": ["/full/path/to/server.py"],
      "env": {"OPENWEATHER_API_KEY": "key"}
    }
  }
}
```

## Agent Instructions (Best Practices)

Add these instructions to your Trimble agent for better weather responses:

```
Weather Data Instructions:
1. Always specify location clearly (city, country code)
2. Use metric or imperial units based on user preference
3. For construction/outdoor work, consider:
   - Temperature extremes (too hot/cold to work)
   - Precipitation (rain, snow impact)
   - Wind speed (safety concerns)
   - Visibility conditions
4. Provide actionable recommendations
5. When forecasting, mention probability of precipitation
6. For air quality queries, explain AQI levels
```

## API Endpoints Reference

### Trimble Platform API

**Create Agent:**
```
POST https://agents.trimble-ai.com/v1/agents
```

**Update Agent (Add Weather MCP):**
```
PATCH https://agents.trimble-ai.com/v1/agents/{agentId}
```

**Execute Agent:**
```
POST https://agents.trimble-ai.com/v1/agents/{agentId}/runs
```

**Get Execution Results:**
```
GET https://agents.trimble-ai.com/v1/agents/{agentId}/runs/{runId}
```

## Deployment Options

### Option 1: Local Development
- Run MCP server on your development machine
- Good for testing and development
- Agent connects to local server

### Option 2: Cloud Deployment
- Deploy MCP server to cloud (AWS, Azure, GCP)
- More reliable for production
- Better for team access

### Option 3: Trimble-Hosted (if available)
- Check if Trimble platform can host the MCP server
- Simplest deployment
- Managed by Trimble

## Troubleshooting

### Agent can't access weather tools

**Check:**
1. MCP server path is absolute, not relative
2. Python is available in the execution environment
3. OpenWeather API key is set correctly
4. Dependencies are installed: `pip install -e .`

**Test the server manually:**
```bash
cd weather-mcp-server
export OPENWEATHER_API_KEY="your_key"
python server.py
# Should start without errors
```

### Weather data is stale

The server caches responses for 10 minutes. To adjust:
```python
# In server.py, line ~21
self.cache_ttl = 300  # Change to 5 minutes
```

### API rate limits

Free tier: 1,000 calls/day, 60/minute
- Server caching helps reduce calls
- Consider upgrading for high-volume use
- Monitor usage at https://home.openweathermap.org/

### Authentication errors

```
Error: "API key not configured"
```
**Solution:** Ensure `OPENWEATHER_API_KEY` is in the env section of agent config

```
Error: "401 Unauthorized"
```
**Solution:** 
- Check API key is correct
- Wait a few hours after signup (key activation)
- Verify at https://home.openweathermap.org/api_keys

## Complete Example

Here's a complete working example:

```python
import requests
import os

# Your API keys
TRIMBLE_API_KEY = os.getenv("TRIMBLE_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
SERVER_PATH = "/Users/abhalek/Documents/Agentic Platform/MCPs/weather-mcp-server/server.py"

# 1. Create agent with weather MCP
agent_response = requests.post(
    "https://agents.trimble-ai.com/v1/agents",
    headers={
        "Authorization": f"Bearer {TRIMBLE_API_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "name": "Construction Weather Assistant",
        "description": "AI assistant for construction weather monitoring",
        "model": "gpt-4",
        "instructions": """You are a construction weather assistant. 
        Use weather data to help with construction planning and safety.
        Always consider weather impact on outdoor construction activities.""",
        "mcp_servers": {
            "weather": {
                "command": "python",
                "args": [SERVER_PATH],
                "env": {
                    "OPENWEATHER_API_KEY": OPENWEATHER_API_KEY
                }
            }
        }
    }
)

agent = agent_response.json()
agent_id = agent["id"]
print(f"✅ Created agent: {agent_id}")

# 2. Execute agent with weather query
run_response = requests.post(
    f"https://agents.trimble-ai.com/v1/agents/{agent_id}/runs",
    headers={
        "Authorization": f"Bearer {TRIMBLE_API_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "input": "What's the weather forecast for our Seattle construction site this week? Should we be concerned about any weather that could delay outdoor work?"
    }
)

run = run_response.json()
run_id = run["id"]
print(f"✅ Started execution: {run_id}")

# 3. Get results
import time
time.sleep(5)  # Wait for execution

result_response = requests.get(
    f"https://agents.trimble-ai.com/v1/agents/{agent_id}/runs/{run_id}",
    headers={"Authorization": f"Bearer {TRIMBLE_API_KEY}"}
)

result = result_response.json()
print(f"\n📊 Agent Response:\n{result['output']}")
```

## Monitoring & Logs

### View Agent Logs
```bash
curl https://agents.trimble-ai.com/v1/agents/AGENT_ID/logs \
  -H "Authorization: Bearer YOUR_TRIMBLE_API_KEY"
```

### Monitor MCP Server
The server logs to stdout. To capture logs:
```json
{
  "env": {
    "OPENWEATHER_API_KEY": "key",
    "LOG_FILE": "/var/log/weather-mcp.log",
    "LOG_LEVEL": "DEBUG"
  }
}
```

## Security Best Practices

1. **Never commit API keys** - Use environment variables
2. **Rotate keys regularly** - Both Trimble and OpenWeather
3. **Use least privilege** - Only enable needed tools
4. **Monitor usage** - Track API calls and costs
5. **Secure the server** - If deployed to cloud, restrict access

## Support & Resources

- **Trimble AI Platform Docs:** https://agents.trimble-ai.com/docs
- **OpenWeatherMap API:** https://openweathermap.org/api
- **Weather MCP README:** [README.md](./README.md)
- **Quick Start Guide:** [QUICKSTART.md](./QUICKSTART.md)

## Next Steps

1. ✅ Get your Trimble API key
2. ✅ Get your OpenWeatherMap API key (free)
3. ✅ Create an agent with weather MCP configured
4. ✅ Test with a weather query
5. ✅ Deploy to production

**Questions?** Check the [Trimble AI Platform documentation](https://agents.trimble-ai.com/docs) or see the PDF: `Configuring Tools for the Agent (1).pdf`

---

**Ready to integrate?** Follow the steps above and your Trimble agents will have weather superpowers! ⚡🌤️

