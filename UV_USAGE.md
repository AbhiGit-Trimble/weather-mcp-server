# Using UV for Dependency Management

This project uses `uv` for fast, modern Python dependency management.

## Installation

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Common Commands

### Setup
```bash
# Install dependencies
uv sync
```

### Running
```bash
# Run server locally
uv run python my_server.py

# Run with gunicorn (production)
uv run gunicorn my_server:app -c gunicorn.conf.py

# Or use the startup script
./startup-gunicorn.sh
```

### Managing Dependencies

```bash
# Add a new dependency
uv add requests

# Remove a dependency
uv remove requests

# Update all dependencies
uv lock --upgrade

# Show dependency tree
uv tree
```

## Deployment (Render)

Render will automatically:
1. Install `uv` via pip
2. Run `uv sync` to install dependencies
3. Start server with `uv run gunicorn`

All configured in `render.yaml`!

## Why UV?

- **10-100x faster** than pip
- **Automatic lock file** (`uv.lock`) for reproducibility
- **Better dependency resolution**
- **Modern Python tooling**
