@echo off
title Audio Clicker - Easy Setup
color 0A
echo.
echo ===============================================
echo      Remote Audio Clicker Setup
echo        with VRChat OSC Support
echo ===============================================
echo.

echo [1/3] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found! Please install Python from python.org
    echo    Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)
echo SUCCESS: Python found!

echo.
echo [2/3] Installing required packages...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Package installation failed!
    pause
    exit /b 1
)
echo SUCCESS: Packages installed!

echo.
echo [3/3] Building standalone executable...
python build_standalone.py
if %errorlevel% neq 0 (
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo SUCCESS: Setup Complete!
echo.
echo ===============================================
echo  Your AudioClicker is ready!
echo.
echo  Find your portable app in: AudioClicker_Distribution
echo  Run: Start_AudioClicker.bat
echo  VRChat: Follow VRChat_Setup_Guide.txt
echo  Share: http://localhost:5000
echo ===============================================
echo.
echo Press any key to open the distribution folder...
pause >nul
explorer AudioClicker_Distribution