# 🖱️ Remote Audio Clicker with VRChat OSC

A fun Python Flask web application that lets your friends remotely trigger audio sounds on your computer AND control your VRChat avatar! Perfect for interactive streaming, VRChat socializing, or just having remote fun with friends.

## ✨ Features

- **🌐 Web Interface**: Beautiful, responsive web page with a big clickable button
- **🔗 REST API**: Direct HTTP endpoints for programmatic access
- **🎵 Audio Playback**: Custom sound support with system beep fallback
- **🎮 VRChat Integration**: Full OSC support for avatar parameter control
- **📊 Click Statistics**: Track total clicks and timing
- **🔄 Real-time Updates**: Live stats updates every 30 seconds
- **� Standalone Executable**: Portable .exe that runs anywhere
- **�🛡️ Cross-platform**: Works on Windows, macOS, and Linux

## 🚀 Quick Start (Standalone)

### Option 1: Use Pre-built Executable
1. **Download** the `AudioClicker_Distribution` folder
2. **Run** `Start_AudioClicker.bat`
3. **Visit** `http://localhost:5000` in your browser
4. **Share** your IP address with friends!

### Option 2: Build from Source
1. **Run** `setup.bat` (Windows) or follow manual setup below
2. **Copy** the generated `AudioClicker_Distribution` folder to your main PC
3. **Launch** with `Start_AudioClicker.bat`

## 🎮 VRChat Integration Setup

### Step 1: Enable OSC in VRChat
1. Open VRChat Settings
2. Go to OSC section
3. Enable OSC
4. Note: VRChat must be running for OSC to work

### Step 2: Add Avatar Parameters
Add these parameters to your avatar in Unity:

**Bool Parameters:**
- `RemoteClick` - Main trigger (momentary)
- `ClickTrigger` - Standard click trigger
- `SpecialTrigger` - Special effect trigger

**Int Parameters:**
- `ClickCount` - Total click counter

### Step 3: Create Avatar Animations
1. In your avatar's Animator Controller, create new Bool parameters
2. Add transitions triggered by these parameters
3. Create fun animations/effects (facial expressions, gestures, particle effects, etc.)
4. Upload your avatar to VRChat

### Step 4: Test OSC Connection
- Visit `http://localhost:5000/vrchat/test-osc`
- Check `http://localhost:5000/vrchat/status` for connection info
- Look for parameter changes in VRChat's avatar menu

## 🌐 API Usage

### Basic Click Trigger
```bash
curl -X POST http://localhost:5000/click \
  -H "Content-Type: application/json" \
  -d "{}"
```

### VRChat Enhanced Click
```bash
curl -X POST http://localhost:5000/vrchat/click \
  -H "Content-Type: application/json" \
  -d '{"type": "special", "intensity": 1.0}'
```

### Custom VRChat Parameters
```bash
curl -X POST http://localhost:5000/vrchat/click \
  -H "Content-Type: application/json" \
  -d '{
    "type": "custom",
    "vrchat_params": {
      "MyCustomParam": true,
      "EmoteIndex": 5
    }
  }'
```

### Get Status
```bash
curl http://localhost:5000/vrchat/status
```

## 📱 How Friends Can Use It

### Option 1: Web Interface
- Send them your computer's IP: `http://YOUR_IP:5000`
- They click the big button on the web page
- Audio plays AND your VRChat avatar reacts instantly!
- **No ngrok warning page** - direct access when using public tunnels!

### Option 2: Direct API Calls
Friends can trigger effects programmatically:

**Python:**
```python
import requests
requests.post("http://YOUR_IP:5000/vrchat/click", json={"type": "special"})
```

**JavaScript:**
```javascript
fetch('http://YOUR_IP:5000/vrchat/click', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({type: 'special'})
});
```

## 🔧 Manual Installation (Advanced Users)

```bash
# Clone repository
git clone [your-repo-url]
cd remote-audio-clicker

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py
```

### Building Standalone Executable
```bash
# Build executable
python build_standalone.py

# Your portable app will be in: AudioClicker_Distribution/
```

## 📁 Project Structure

```
remote-audio-clicker/
├── app.py                          # Main Flask application with OSC
├── build_standalone.py             # Build script for executable
├── setup.bat                       # Easy Windows setup
├── requirements.txt                # Python dependencies
├── templates/
│   └── index.html                  # Web interface
├── static/
│   └── click.wav                   # Custom audio file (optional)
└── README.md                       # This file

AudioClicker_Distribution/          # Generated standalone package
├── AudioClicker.exe               # Portable executable
├── Start_AudioClicker.bat         # Easy launcher
├── VRChat_Setup_Guide.txt         # VRChat setup instructions
└── README.md                      # Documentation
```

## 🎵 Adding Custom Sounds

1. Place your `.wav` audio file in the `static/` directory
2. Rename it to `click.wav`
3. Restart the server

If no custom sound is found, the app will use a system beep as fallback.

## 🔐 Network Setup

### Finding Your IP Address
**Windows:**
```cmd
ipconfig | findstr IPv4
```

**macOS/Linux:**
```bash
ifconfig | grep "inet "
```

### Firewall Configuration
Make sure these ports are open:
- **5000** - Web interface and API
- **9000** - VRChat OSC output
- **9001** - VRChat OSC input (if using bidirectional)

### Router Configuration
For friends outside your network:
1. Forward port 5000 to your computer's local IP
2. Share your public IP address
3. Use format: `http://YOUR_PUBLIC_IP:5000`

## 🎮 VRChat Avatar Ideas

### Simple Reactions
- **Facial expressions** triggered by clicks
- **Hand gestures** or wave animations
- **Eye color changes** or blinking patterns

### Advanced Effects
- **Particle systems** (hearts, stars, confetti)
- **Clothing color changes**
- **Accessory toggles** (hats, glasses, etc.)
- **Dance moves** or poses

### Interactive Elements
- **Click counter display** on avatar (using TextMesh Pro)
- **Different reactions** based on click count
- **Special effects** for milestone numbers

## ⚠️ Troubleshooting

### Audio Issues
- Check if `pygame` is installed correctly
- Verify audio file exists and is valid `.wav`
- Test system audio settings

### VRChat OSC Issues
- Ensure VRChat OSC is enabled in settings
- Check that VRChat is running
- Verify avatar parameters are uploaded correctly
- Test with `/vrchat/test-osc` endpoint

### Network Access Issues
- Check firewall settings for port 5000
- Verify you're using the correct IP address
- Ensure Flask server shows "Running on all addresses (0.0.0.0)"

### Executable Issues
- Run `setup.bat` to rebuild
- Check Python and pip are installed
- Try running `python app.py` directly for debugging

## 🔐 Security Notes

- This is a development server - don't expose to public internet without authentication
- Consider using HTTPS for production environments
- Be mindful of who has access to trigger sounds/avatar reactions

## 🎯 Use Cases

### Streaming
- **Viewer interaction** with your VRChat avatar
- **Sound alerts** for donations/follows
- **Interactive comedy** moments

### Social VRChat
- **Friends can mess with you** remotely
- **Party games** and interactive activities
- **Long-distance** social interaction

### Content Creation
- **Remote controlled** avatar reactions
- **Synchronized** audio/visual effects
- **Interactive storytelling**

## 🤝 Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements!

## 📄 License

This project is open source. Have fun with it!

---

**Made with ❤️ for VRChat social interaction and remote fun!** 🎉🎮