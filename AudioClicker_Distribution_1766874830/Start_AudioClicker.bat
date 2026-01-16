@echo off
title Remote Audio Clicker with VRChat OSC
color 0A
echo.
echo ===============================================
echo      Remote Audio Clicker
echo        with VRChat OSC Support
echo ===============================================
echo.

echo [1/3] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    echo.
    echo Please install Python from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo SUCCESS: Python found!
echo.
echo [2/3] Installing/checking dependencies...
pip install -q flask pygame python-osc
if %errorlevel% neq 0 (
    echo WARNING: Some packages may have failed to install
    echo The app may still work with existing packages
)

echo.
echo [3/3] Starting Remote Audio Clicker...
echo.
echo ===============================================
echo  Web Interface: http://localhost:5000
echo  VRChat OSC: Enabled (if VRChat is running)
echo  Share with friends: http://YOUR_IP:5000
echo.
echo  VRChat Setup:
echo    1. Enable OSC in VRChat Settings
echo    2. Add Bool parameters: RemoteClick, ClickTrigger
echo    3. Add Int parameter: ClickCount
echo    4. Test: http://localhost:5000/vrchat/test-osc
echo ===============================================
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py