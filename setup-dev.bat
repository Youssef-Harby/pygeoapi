@echo off
setlocal enabledelayedexpansion

REM pygeoapi Development Setup Script for Windows
REM Checks for uv installation, installs if needed, syncs dependencies, and runs dev server

echo pygeoapi Development Setup
echo ==============================
echo.

REM Check if uv is installed
uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo uv not found. Installing uv...
    
    REM Check if PowerShell is available
    powershell -Command "Get-Command powershell" >nul 2>&1
    if %errorlevel% neq 0 (
        echo PowerShell not found. Please install uv manually.
        pause
        exit /b 1
    )
    
    REM Install uv using PowerShell
    powershell -Command "irm https://astral.sh/uv/install.ps1 | iex"
    
    REM Add uv to PATH for current session
    set "PATH=%USERPROFILE%\.cargo\bin;%PATH%"
    
    REM Check if installation was successful
    uv --version >nul 2>&1
    if !errorlevel! neq 0 (
        echo Failed to install uv. Please install manually.
        pause
        exit /b 1
    )
) else (
    echo uv is already installed
)

echo.
echo Syncing project dependencies...
uv sync
if %errorlevel% neq 0 (
    echo Failed to sync dependencies.
    pause
    exit /b 1
)

echo.
echo Installing all optional dependency groups...
uv sync --group admin --group django --group docker --group starlette
if %errorlevel% neq 0 (
    echo Warning: Some optional groups failed to install.
)

echo.
echo Setting up environment variables...
set PYGEOAPI_CONFIG=pygeoapi-config.yml
set PYGEOAPI_OPENAPI=pygeoapi-config.yml

echo.
echo Starting pygeoapi development server...
echo Server will be available at: http://localhost:5001
echo Press Ctrl+C to stop the server
echo.

uv run pygeoapi serve

if %errorlevel% neq 0 (
    echo Server failed to start.
    pause
)