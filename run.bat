@echo off
REM AGENTLENS - Setup and Run Script for Windows
echo ============================================
echo   AGENTLENS - AI Agent Reliability Intel
echo ============================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.10+
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Run the server
echo.
echo Starting AGENTLENS server...
echo Open http://localhost:8000 in your browser
echo.
python -m agentlens.main

pause
