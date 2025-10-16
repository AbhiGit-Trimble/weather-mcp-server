#!/usr/bin/env python3
"""
Example: Using Weather MCP Server with Trimble Agentic Platform
This script shows how to create and use a Trimble agent with weather capabilities
"""

import requests
import os
import time
import json

# Configuration
TRIMBLE_API_KEY = os.getenv("TRIMBLE_API_KEY", "your_trimble_api_key")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "your_openweather_api_key")
TRIMBLE_API_BASE = "https://agents.trimble-ai.com/v1"
SERVER_PATH = "/Users/abhalek/Documents/Agentic Platform/MCPs/weather-mcp-server/server.py"


def create_weather_agent():
    """Create a Trimble agent with weather MCP capabilities"""
    
    print("🤖 Creating Trimble agent with weather capabilities...")
    
    agent_config = {
        "name": "Construction Weather Assistant",
        "description": "AI assistant for construction site weather monitoring and planning",
        "model": "gpt-4",
        "instructions": """You are a construction weather assistant with access to real-time weather data.
        
Your responsibilities:
1. Monitor weather conditions for construction sites
2. Provide accurate forecasts for project planning
3. Alert about adverse weather conditions
4. Recommend weather-based schedule adjustments
5. Consider safety implications of weather

When answering:
- Always specify location and time
- Use appropriate units for the region
- Highlight safety concerns (extreme temps, high winds, heavy rain)
- Provide actionable recommendations
- Mention probability for forecasts""",
        
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
    
    response = requests.post(
        f"{TRIMBLE_API_BASE}/agents",
        headers={
            "Authorization": f"Bearer {TRIMBLE_API_KEY}",
            "Content-Type": "application/json"
        },
        json=agent_config
    )
    
    if response.status_code == 201:
        agent = response.json()
        print(f"✅ Agent created successfully!")
        print(f"   Agent ID: {agent['id']}")
        print(f"   Name: {agent['name']}")
        return agent
    else:
        print(f"❌ Failed to create agent: {response.status_code}")
        print(f"   Error: {response.text}")
        return None


def execute_agent(agent_id, query):
    """Execute an agent with a weather query"""
    
    print(f"\n💬 Executing agent with query: '{query}'")
    
    response = requests.post(
        f"{TRIMBLE_API_BASE}/agents/{agent_id}/runs",
        headers={
            "Authorization": f"Bearer {TRIMBLE_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "input": query
        }
    )
    
    if response.status_code == 200:
        run = response.json()
        print(f"✅ Execution started")
        print(f"   Run ID: {run['id']}")
        return run
    else:
        print(f"❌ Failed to execute agent: {response.status_code}")
        print(f"   Error: {response.text}")
        return None


def get_execution_result(agent_id, run_id, max_attempts=10):
    """Poll for execution results"""
    
    print(f"\n⏳ Waiting for results...")
    
    for attempt in range(max_attempts):
        response = requests.get(
            f"{TRIMBLE_API_BASE}/agents/{agent_id}/runs/{run_id}",
            headers={
                "Authorization": f"Bearer {TRIMBLE_API_KEY}"
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            status = result.get("status")
            
            if status == "completed":
                print(f"✅ Execution completed!")
                return result
            elif status == "failed":
                print(f"❌ Execution failed: {result.get('error')}")
                return result
            else:
                print(f"   Status: {status} (attempt {attempt + 1}/{max_attempts})")
                time.sleep(2)
        else:
            print(f"❌ Failed to get results: {response.status_code}")
            return None
    
    print(f"⚠️  Timeout waiting for results")
    return None


def display_result(result):
    """Display the agent's response"""
    
    if not result:
        return
    
    print(f"\n" + "="*60)
    print(f"📊 AGENT RESPONSE")
    print(f"="*60)
    print(f"\nStatus: {result.get('status')}")
    print(f"\nOutput:\n{result.get('output', 'No output')}")
    
    # Show which tools were used
    if 'tool_calls' in result:
        print(f"\n🛠️  Tools used:")
        for tool_call in result['tool_calls']:
            print(f"   - {tool_call.get('tool_name')}")
    
    print(f"\n" + "="*60)


def main():
    """Main example workflow"""
    
    print("\n" + "="*60)
    print("🌤️  Weather MCP + Trimble Agentic Platform Example")
    print("="*60)
    
    # Check API keys
    if TRIMBLE_API_KEY == "your_trimble_api_key":
        print("\n⚠️  Please set TRIMBLE_API_KEY environment variable")
        print("   export TRIMBLE_API_KEY='your_key'")
        return
    
    if OPENWEATHER_API_KEY == "your_openweather_api_key":
        print("\n⚠️  Please set OPENWEATHER_API_KEY environment variable")
        print("   export OPENWEATHER_API_KEY='your_key'")
        print("   Get free key at: https://openweathermap.org/api")
        return
    
    # 1. Create agent
    agent = create_weather_agent()
    if not agent:
        return
    
    agent_id = agent['id']
    
    # 2. Example queries
    queries = [
        "What's the weather in Paris right now?",
        "Will it rain in Seattle this week?",
        "Compare weather in New York, London, and Tokyo",
        "What's the air quality in Los Angeles?",
        "Give me a 5-day forecast for Chicago"
    ]
    
    # Try the first query
    query = queries[0]
    run = execute_agent(agent_id, query)
    
    if not run:
        return
    
    # 3. Get results
    result = get_execution_result(agent_id, run['id'])
    
    # 4. Display results
    display_result(result)
    
    # Show other example queries
    print(f"\n💡 Try these other queries:")
    for i, q in enumerate(queries[1:], 1):
        print(f"   {i}. {q}")
    
    print(f"\n✨ Success! Your Trimble agent has weather superpowers!")


if __name__ == "__main__":
    main()

