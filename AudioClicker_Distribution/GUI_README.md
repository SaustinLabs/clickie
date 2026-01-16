# 🎮 Remote Audio Clicker - GUI Server

## 🎨 Beautiful GUI Interface

No more ugly command prompts! This version includes a clean, modern GUI with:

### ✨ Features

- **🎯 One-Click Start/Stop** - Simple buttons to control the server
- **🌍 Public URL Display** - Ngrok tunnel URL shown prominently with copy button
- **📊 Live Statistics** - Real-time click counts updating automatically
- **📝 Activity Log** - See what's happening in real-time
- **🌐 Quick Browser Access** - Open the web interface directly from GUI
- **💜 Dark Theme** - Easy on the eyes with modern colors

### 🚀 How to Use

#### Option 1: Double-click launcher (Easiest)
1. Double-click `Start_GUI_Server.bat`
2. The GUI window will open
3. Click "▶️ Start Server"
4. Share the Public URL that appears!

#### Option 2: Python directly
```bash
python gui_server.py
```

### 📸 GUI Overview

**Status Section:**
- Shows if server is running or stopped
- Green ✅ when active, red ⭕ when stopped

**Control Buttons:**
- ▶️ Start Server - Launches Flask and ngrok
- ⏹️ Stop Server - Stops everything

**Public URL Section:**
- Displays your ngrok tunnel URL
- 📋 Copy URL - Copies to clipboard
- 🌐 Open in Browser - Opens in default browser

**Statistics:**
- Total Clicks (all time)
- Today's Clicks
- Local URL (for same network access)

**Activity Log:**
- Shows server events in real-time
- Timestamps for everything
- Helpful status messages

### 🔧 Configuration

The GUI uses the same settings from `app.py`:
- Ngrok auth token (automatically detected)
- Sound files
- Rate limiting
- All other settings

### 💡 Tips

1. **Keep the GUI window open** while server is running
2. **Use the Copy URL button** to easily share with friends
3. **Watch the Activity Log** to see clicks happening in real-time
4. **Click the Local URL** to test on your own computer first

### ⚠️ Notes

- The GUI must stay open for the server to run
- Closing the window stops the server
- You can minimize it to system tray (stays in taskbar)
- The old command-line version (`app.py`) still works if you prefer

### 🎨 Color Scheme

- Background: Dark blue-gray (#2b2d42)
- Success: Bright green (#06ffa5)
- Info: Cyan (#00b4d8)
- Error: Red (#ef233c)
- Accent: Light gray (#8d99ae)

### 🐛 Troubleshooting

**GUI doesn't open:**
- Make sure Python is installed
- Try running `python gui_server.py` directly

**Tunnel URL not appearing:**
- Check your ngrok auth token in `app.py`
- Make sure you have internet connection
- Wait ~5 seconds after starting server

**Server won't start:**
- Make sure port 5000 isn't already in use
- Check if another instance is running
- Try restarting your computer

### 🆚 GUI vs Command Line

**Use GUI when:**
- ✅ You want a clean, pretty interface
- ✅ You need easy access to the URL
- ✅ You want to see stats at a glance
- ✅ You don't like looking at terminals

**Use Command Line when:**
- 🖥️ You're comfortable with terminals
- 🖥️ You want to see detailed Flask logs
- 🖥️ You're running on a server without GUI
- 🖥️ You want to redirect logs to a file

Both versions have identical functionality - it's just about preference!

---

Made with 💜 for long distance relationships
