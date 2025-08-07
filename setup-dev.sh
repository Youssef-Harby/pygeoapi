#!/bin/bash

# pygeoapi Development Setup Script
# Checks for uv installation, installs if needed, syncs dependencies, and runs dev server

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}pygeoapi Development Setup${NC}"
echo "=============================="

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}uv not found. Installing uv...${NC}"
    
    # Detect OS and install uv accordingly
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl -LsSf https://astral.sh/uv/install.sh | sh
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install uv
        else
            curl -LsSf https://astral.sh/uv/install.sh | sh
        fi
    else
        echo -e "${RED}Unsupported OS. Please install uv manually.${NC}"
        exit 1
    fi
    
    # Source the shell profile to make uv available
    export PATH="$HOME/.cargo/bin:$PATH"
    
    if ! command -v uv &> /dev/null; then
        echo -e "${RED}Failed to install uv. Please install manually.${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}uv is already installed${NC}"
fi

echo -e "${YELLOW}Syncing project dependencies...${NC}"
uv sync

echo -e "${YELLOW}Installing all optional dependency groups...${NC}"
uv sync --group admin --group django --group docker --group starlette

echo -e "${YELLOW}Setting up environment variables...${NC}"
export PYGEOAPI_CONFIG="pygeoapi-config.yml"
export PYGEOAPI_OPENAPI="pygeoapi-config.yml"

echo -e "${GREEN}Starting pygeoapi development server...${NC}"
echo "Server will be available at: http://localhost:5001"
echo "Press Ctrl+C to stop the server"
echo ""

uv run pygeoapi serve