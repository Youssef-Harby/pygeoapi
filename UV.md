# UV Development Guide

Quick reference for working with `uv` in the pygeoapi project.

## Installation

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# macOS with Homebrew
brew install uv

# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex
```

## Project Setup

```bash
# Sync all dependencies
uv sync

# Install with optional groups
uv sync --group admin --group django --group docker --group starlette
```

## Running Commands

```bash
# Run pygeoapi server
PYGEOAPI_CONFIG=pygeoapi-config.yml PYGEOAPI_OPENAPI=pygeoapi-config.yml uv run pygeoapi serve

# Run any Python script
uv run python script.py

# Run with additional dependencies
uv run --with requests python script.py
```

## Dependency Management

```bash
# Add dependency
uv add package-name

# Add to specific group
uv add --group dev pytest

# Remove dependency
uv remove package-name

# Update dependencies
uv sync --upgrade
```

## Environment Management

```bash
# Activate virtual environment
source .venv/bin/activate  # Unix
.venv\Scripts\activate     # Windows

# Check Python version
uv python list

# Install specific Python version
uv python install 3.11
```

## Optional Dependency Groups

- `admin` - Administrative tools (gunicorn, etc.)
- `django` - Django framework support
- `docker` - Docker-related dependencies
- `starlette` - Starlette ASGI framework
- `dev` - Development tools (default group)

## Common Tasks

```bash
# Run tests
uv run pytest

# Format code
uv run black .

# Lint code
uv run flake8

# Build package
uv build

# Check outdated packages
uv tree --outdated
```

## Configuration Files

- `pyproject.toml` - Project metadata and dependencies
- `uv.lock` - Locked dependency versions
- `.python-version` - Python version pin
- `pygeoapi-config.yml` - Application configuration

## Troubleshooting

```bash
# Clear cache
uv cache clean

# Reinstall environment
rm -rf .venv && uv sync

# Check environment status
uv pip list

# Debug dependency resolution
uv sync --verbose
```

## Performance Tips

- Use `uv run` for one-off commands
- Activate environment for multiple commands
- Use `--no-dev` to skip development dependencies
- Use `--frozen` to skip lock file updates