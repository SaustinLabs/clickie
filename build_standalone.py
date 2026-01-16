"""
Build script for Remote Audio Clicker with VRChat OSC support
Creates a standalone executable that can run on any Windows PC
"""

import os
import subprocess
import sys
import shutil
import time
import stat
from pathlib import Path

def build_executable():
    """Build standalone executable using PyInstaller"""
    print("🔨 Building standalone executable...")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",                    # Single executable file
        "--windowed",                   # No console window (comment out for debugging)
        "--name", "AudioClicker",       # Executable name
        "--icon", "icon.ico",          # App icon (if exists)
        "--add-data", "templates;templates",  # Include templates folder
        "--add-data", "static;static",        # Include static folder
        "--hidden-import", "pygame",
        "--hidden-import", "pythonosc",
        "--hidden-import", "flask",
        "app.py"
    ]
    
    # Remove icon parameter if icon file doesn't exist
    if not os.path.exists("icon.ico"):
        cmd.remove("--icon")
        cmd.remove("icon.ico")
        print("⚠️ No icon.ico found, building without icon")
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ Executable built successfully!")
        print("📁 Find your executable in: dist/AudioClicker.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False
    except FileNotFoundError:
        print("❌ PyInstaller not found. Install with: pip install pyinstaller")
        return False

def create_distribution_package():
    """Create a complete distribution package"""
    print("\n📦 Creating distribution package...")
    
    dist_dir = Path("AudioClicker_Distribution")
    
    # Try to clean and create distribution directory with better error handling
    if dist_dir.exists():
        try:
            print("🧹 Cleaning existing distribution folder...")
            
            # Remove readonly attributes first
            for root, dirs, files in os.walk(dist_dir):
                for d in dirs:
                    try:
                        os.chmod(os.path.join(root, d), stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                    except:
                        pass
                for f in files:
                    try:
                        file_path = os.path.join(root, f)
                        os.chmod(file_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                    except:
                        pass
            
            # Now try to remove the directory
            shutil.rmtree(dist_dir)
        except PermissionError:
            print("⚠️ Distribution folder is in use, trying alternative approach...")
            try:
                # Try to move it first, then delete
                backup_dir = Path(f"AudioClicker_Distribution_backup_{int(time.time())}")
                dist_dir.rename(backup_dir)
                print(f"📁 Moved existing folder to: {backup_dir}")
                print("💡 You can safely delete the backup folder later")
            except Exception as e:
                print(f"⚠️ Could not clean existing folder: {e}")
                print("📁 Creating new folder with timestamp...")
                dist_dir = Path(f"AudioClicker_Distribution_{int(time.time())}")
    
    # Create the distribution directory
    try:
        dist_dir.mkdir(exist_ok=True)
    except Exception as e:
        print(f"❌ Could not create distribution folder: {e}")
        return
    
    # Copy executable if it exists
    exe_path = Path("dist/AudioClicker.exe")
    if exe_path.exists():
        shutil.copy(exe_path, dist_dir / "AudioClicker.exe")
        print("✅ Executable copied")
    else:
        print("⚠️ Executable not found, copying Python files instead")
        shutil.copy("app.py", dist_dir / "app.py")
        shutil.copytree("templates", dist_dir / "templates")
        if Path("static").exists():
            shutil.copytree("static", dist_dir / "static")
        shutil.copy("requirements.txt", dist_dir / "requirements.txt")
    
    # Create sample sound file directory
    (dist_dir / "static").mkdir(exist_ok=True)
    
    # Copy documentation
    shutil.copy("README.md", dist_dir / "README.md")
    
    # Create VRChat setup guide
    vrchat_guide = """# VRChat OSC Setup Guide

## Quick Setup:
1. Run AudioClicker.exe
2. In VRChat: Settings > OSC > Enable OSC
3. Add these Bool parameters to your avatar:
   - RemoteClick
   - ClickTrigger  
   - SpecialTrigger
4. Add this Int parameter:
   - ClickCount

## Testing:
- Visit http://localhost:5000/vrchat/test-osc to test OSC
- Visit http://localhost:5000/vrchat/status to check connection

## Avatar Animation Setup:
1. In Unity, open your avatar's Animator Controller
2. Create new Bool parameters: RemoteClick, ClickTrigger, SpecialTrigger
3. Create new Int parameter: ClickCount
4. Add transitions triggered by these parameters
5. Create fun animations/effects that respond to remote clicks!

## Common Issues:
- Make sure VRChat OSC is enabled in settings
- Check firewall isn't blocking port 9000/9001
- Parameters must be added to BOTH Unity project AND uploaded avatar
"""
    
    with open(dist_dir / "VRChat_Setup_Guide.txt", "w") as f:
        f.write(vrchat_guide)
    
    # Create launcher batch file for easy startup
    launcher_content = """@echo off
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

python app.py"""
    
    with open(dist_dir / "Start_AudioClicker.bat", "w") as f:
        f.write(launcher_content)
    
    print("✅ Distribution package created!")
    print(f"📁 Package location: {dist_dir.absolute()}")
    print("\n📋 Package contents:")
    for item in dist_dir.iterdir():
        print(f"   • {item.name}")

def main():
    """Main build process"""
    print("🎮 Remote Audio Clicker Build System")
    print("===================================")
    
    # Check if we're in the right directory
    if not os.path.exists("app.py"):
        print("❌ app.py not found. Please run this script from the project directory.")
        sys.exit(1)
    
    print("\n1. Building executable...")
    build_success = build_executable()
    
    print("\n2. Creating distribution package...")
    create_distribution_package()
    
    print("\n🎉 Build Complete!")
    print("\nNext steps:")
    print("1. Copy the 'AudioClicker_Distribution' folder to your main PC")
    print("2. Run 'Start_AudioClicker.bat' to launch")
    print("3. Follow 'VRChat_Setup_Guide.txt' for VRChat integration")
    print("4. Share http://YOUR_IP:5000 with friends!")
    
    if build_success:
        print("\n💡 Pro tip: The .exe file is portable - just copy it anywhere and run!")

if __name__ == "__main__":
    main()