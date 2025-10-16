"""
Gunicorn configuration file for production deployment
"""
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"

# Worker processes
workers = int(os.getenv('WORKERS', '2'))
worker_class = "uvicorn.workers.UvicornWorker"

# Logging
loglevel = os.getenv('LOG_LEVEL', 'info')
accesslog = '-'
errorlog = '-'

# Process naming
proc_name = 'weather-mcp-server'

# Worker timeout
timeout = int(os.getenv('TIMEOUT', '120'))
keepalive = int(os.getenv('KEEPALIVE', '5'))

# Preload app for better performance
preload_app = True

# Maximum requests per worker (helps prevent memory leaks)
max_requests = int(os.getenv('MAX_REQUESTS', '1000'))
max_requests_jitter = int(os.getenv('MAX_REQUESTS_JITTER', '50'))
