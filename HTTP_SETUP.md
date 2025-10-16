# Weather MCP Server - HTTP Version

This is the HTTP-based version of the Weather MCP Server for use with Trimble Agentic Platform.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements-http.txt
```

### 2. Set Your API Key

```bash
export OPENWEATHER_API_KEY="f3d6a55b5c91fc1c77cebec3ec5f46a1"
```

### 3. Run the HTTP Server

```bash
python server_http.py
```

The server will start on `http://localhost:8000`

## 📝 Use with Trimble UI

### Step 1: Start the Server

```bash
cd weather-mcp-server
export OPENWEATHER_API_KEY="f3d6a55b5c91fc1c77cebec3ec5f46a1"
python server_http.py
```

You should see:
```
🌤️  Weather MCP Server (HTTP)
📍 Running on: http://0.0.0.0:8000
✨ Ready to serve weather data!
```

### Step 2: Get Your Server URL

**For local testing:**
```
http://localhost:8000/mcp
```

**For production (deploy to cloud):**
```
https://your-domain.com/mcp
```

### Step 3: Configure in Trimble UI

In the Trimble "Tools" section:

```
Tool Type: MCP
Name: Weather Tool
URL: http://localhost:8000/mcp
Authentication: None
```

Click "Save Tool"

## 🌐 API Endpoints

### MCP Protocol Endpoints

```
GET  /mcp/tools              - List available tools
POST /mcp/tools/call         - Execute a tool
GET  /mcp/resources          - List available resources
POST /mcp/resources/read     - Read a resource
```

### Health Endpoints

```
GET  /                       - Server info
GET  /health                 - Health check
```

## 🧪 Test the Server

### Test with curl

```bash
# List available tools
curl http://localhost:8000/mcp/tools

# Get current weather
curl -X POST http://localhost:8000/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "get_current_weather",
    "arguments": {
      "location": "Paris,FR",
      "units": "metric"
    }
  }'
```

### Test in Browser

Open: http://localhost:8000

You should see:
```json
{
  "name": "Weather MCP Server",
  "version": "1.0.0",
  "protocol": "MCP over HTTP",
  "status": "running"
}
```

## 🚢 Deployment Options

### Option 1: Local (Development)

Run locally for testing:
```bash
python server_http.py
```

**Use in Trimble:**
```
URL: http://localhost:8000/mcp
```

### Option 2: ngrok (Quick Public URL)

For testing with external services:

```bash
# Install ngrok: https://ngrok.com/download

# Start server
python server_http.py

# In another terminal, expose it
ngrok http 8000
```

You'll get a public URL like: `https://abc123.ngrok.io`

**Use in Trimble:**
```
URL: https://abc123.ngrok.io/mcp
```

### Option 3: Cloud Deployment

#### Deploy to Railway.app (Free Tier)

1. Create `Procfile`:
```
web: python server_http.py
```

2. Push to Railway or use Railway CLI
3. Get your URL: `https://your-app.railway.app`

#### Deploy to Render.com (Free Tier)

1. Connect GitHub repo
2. Set build command: `pip install -r requirements-http.txt`
3. Set start command: `python server_http.py`
4. Add environment variable: `OPENWEATHER_API_KEY`
5. Get your URL: `https://your-app.onrender.com`

#### Deploy to Fly.io (Free Tier)

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Initialize
fly launch

# Deploy
fly deploy
```

## ⚙️ Configuration

### Environment Variables

```bash
# Required
export OPENWEATHER_API_KEY="your_key"

# Optional
export PORT=8000              # Server port (default: 8000)
export HOST="0.0.0.0"        # Server host (default: 0.0.0.0)
export CACHE_TTL=600         # Cache duration in seconds
export LOG_LEVEL=INFO        # Logging level
```

### Custom Port

```bash
export PORT=3000
python server_http.py
```

Server will run on `http://localhost:3000`

## 📊 Available Tools

All 7 weather tools are available via HTTP:

1. **get_current_weather** - Current weather for any location
2. **get_forecast** - 5-day forecast
3. **search_location** - Find locations
4. **get_weather_by_coordinates** - Weather by GPS
5. **get_air_quality** - Air quality data
6. **compare_weather** - Compare multiple cities

## 🔧 Troubleshooting

### Server won't start

```bash
# Check if port is in use
lsof -i :8000

# Use different port
export PORT=8001
python server_http.py
```

### "API key not configured"

```bash
# Make sure environment variable is set
echo $OPENWEATHER_API_KEY

# Set it if empty
export OPENWEATHER_API_KEY="f3d6a55b5c91fc1c77cebec3ec5f46a1"
```

### Trimble can't connect

- ✅ Make sure server is running
- ✅ Check firewall settings
- ✅ For localhost, Trimble must run on same machine
- ✅ For remote access, deploy to cloud and use public URL

### CORS errors

The server has CORS enabled for all origins. If you still get errors:

1. Check if you're using HTTPS in production
2. Verify the URL in Trimble matches your server URL
3. Check browser console for specific errors

## 🔒 Security Notes

### For Production:

1. **Use HTTPS** - Deploy behind SSL/TLS
2. **Add authentication** - Use API keys or tokens
3. **Rate limiting** - Implement rate limits
4. **Restrict CORS** - Limit allowed origins
5. **Secure API keys** - Use secrets management

### Example with Authentication:

Add to `server_http.py`:

```python
from fastapi import Header, HTTPException

async def verify_token(x_api_key: str = Header(...)):
    if x_api_key != os.getenv("MCP_API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API key")
```

Then in Trimble UI:
```
Authentication: raw actor token
Token: your_mcp_api_key
```

## 📱 Example Usage in Trimble

Once configured, your Trimble agent can:

```
Agent: "What's the weather in Paris?"
↓
Trimble calls: POST /mcp/tools/call
↓
Tool: get_current_weather
Arguments: {"location": "Paris,FR"}
↓
Returns: Temperature, conditions, etc.
```

## 🎯 Complete Setup Example

```bash
# 1. Navigate to directory
cd weather-mcp-server

# 2. Install dependencies
pip install -r requirements-http.txt

# 3. Set API key
export OPENWEATHER_API_KEY="f3d6a55b5c91fc1c77cebec3ec5f46a1"

# 4. Run server
python server_http.py

# 5. In another terminal, test it
curl http://localhost:8000/health

# 6. In Trimble UI, configure:
#    Tool Type: MCP
#    Name: Weather Tool
#    URL: http://localhost:8000/mcp
#    Authentication: None

# 7. Test in Trimble agent:
#    "What's the weather in London?"
```

## 📚 Next Steps

1. ✅ Test locally first
2. ✅ Deploy to cloud for production
3. ✅ Add authentication if needed
4. ✅ Monitor usage and logs
5. ✅ Scale as needed

---

**Questions?** The HTTP server is fully compatible with the Trimble UI MCP tool configuration! 🚀

