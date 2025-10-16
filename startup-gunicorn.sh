#!/bin/bash

# Set default values
export HOST=${HOST:-"0.0.0.0"}
export PORT=${PORT:-"8000"}
export WORKERS=${WORKERS:-"2"}

# Start the Weather MCP server with Gunicorn via uv
uv run gunicorn my_server:app -c gunicorn.conf.py
