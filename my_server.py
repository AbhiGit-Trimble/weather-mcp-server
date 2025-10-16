import os
from fastmcp import FastMCP
from tools import register_all_tools

# Create a FastMCP server instance
mcp = FastMCP("Weather MCP Server")

# Register all tools from the tools package
register_all_tools(mcp)


@mcp.resource("config://server")
def get_server_config():
    """
    Provide server configuration as a resource.
    """
    return {
        "server_name": "Weather MCP Server",
        "api_configured": bool(os.getenv("OPENWEATHER_API_KEY")),
        "base_url": "https://api.openweathermap.org/data/2.5",
        "cache_ttl": 600
    }


# Create ASGI application for deployment
# FastMCP provides an ASGI-compatible HTTP app via the http_app() method
app = mcp.http_app()

if __name__ == "__main__":
    # For local development and production deployment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))

    # Run with HTTP transport for ASGI compatibility
    mcp.run(transport="http", host=host, port=port)
