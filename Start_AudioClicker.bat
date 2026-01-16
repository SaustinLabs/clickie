@echo off
title Remote Audio Clicker with VRChat OSC
color 0A
echo.
echo ===============================================
echo      Remote Audio Clicker
echo        with VRChat OSC Support
echo ===============================================
echo.

echo [1/4] Checking Python installation...
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
echo [2/4] Installing/checking dependencies...
pip install -q flask pygame python-osc pyngrok
if %errorlevel% neq 0 (
    echo WARNING: Some packages may have failed to install
    echo The app may still work with existing packages
)

echo.
echo [3/4] Setting up public tunnel (no port forwarding needed)...
echo.
echo Choose your tunneling option:
echo   1. ngrok (recommended - requires free signup at ngrok.com)
echo   2. LocalTunnel (no signup required)
echo   3. Skip tunneling (local network only)
echo.
set /p tunnel_choice="Enter choice (1-3): "

if "%tunnel_choice%"=="1" (
    echo.
    echo Setting up ngrok tunnel...
    echo NOTE: If this fails, sign up at https://ngrok.com and get your auth token
    echo Then run: ngrok config add-authtoken YOUR_TOKEN
) else if "%tunnel_choice%"=="2" (
    echo.
    echo Setting up LocalTunnel...
    echo Installing localtunnel...
    npm install -g localtunnel 2>nul || echo WARNING: LocalTunnel setup may have failed
)

echo.
echo [4/4] Starting Remote Audio Clicker...
echo.
echo ===============================================
echo  Local Interface: http://localhost:5000
echo  VRChat OSC: Enabled (if VRChat is running)
if not "%tunnel_choice%"=="3" (
    echo  Public URL: Will be displayed below after startup
) else (
    echo  Local Network: http://YOUR_IP:5000
)
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

if "%tunnel_choice%"=="1" (
    echo.
    echo Setting up ngrok tunnel...
    echo NOTE: The Python app will handle ngrok automatically
    echo Your auth token should be set in app.py
) else if "%tunnel_choice%"=="2" (
    start /B npx localtunnel --port 5000
    timeout /t 3 >nul
    echo.
    echo ========== LOCALTUNNEL URL ==========
    echo Check the LocalTunnel window for your public URL
    echo ====================================
    echo.
)

python app.py