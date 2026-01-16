@echo off
title Remote Audio Clicker - GUI Server
cd /d "%~dp0"

echo Starting GUI Server...
echo.

REM Check if virtual environment exists
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    python gui_server.py
) else (
    echo Virtual environment not found. Using system Python...
    python gui_server.py
)

pause
