# ⚡ PiShock Integration Guide

## What is PiShock?

PiShock is a remote shock collar device that can be controlled via API. This integration allows the "Bonk" button to trigger physical feedback for consensual BDSM/kink play.

## 🔐 Safety & Consent

**IMPORTANT:**
- ⚠️ **Only use with explicit consent** from all parties
- ⚠️ Start with **LOW intensity** (10-20) and gradually increase
- ⚠️ Test on yourself first before using on others
- ⚠️ Have a safe word/safe gesture
- ⚠️ Never leave unattended
- ⚠️ Follow PiShock's safety guidelines

## 🛠️ Setup Instructions

### Step 1: Get PiShock Credentials

1. Go to https://pishock.com
2. Create an account or log in
3. Go to **Account Settings**
4. Find your **API Key** - copy this
5. Go to **Shares** section
6. Create a new share code or use existing one
7. Copy the **Sharecode**
8. Copy your **Username**

### Step 2: Configure in GUI

1. Open the GUI server (`Start_GUI_Server.bat`)
2. Click **Start Server**
3. Click the **⚡ PiShock Settings** button
4. Enter your credentials:
   - **Username**: Your PiShock username
   - **API Key**: From account settings
   - **Sharecode**: From shares section
   - **Name**: Display name (e.g., "PiShock")
5. Set default settings:
   - **Operation**: 
     - 0 = Shock (⚡)
     - 1 = Vibrate (📳)
     - 2 = Beep (🔊)
   - **Intensity**: 0-100 (start LOW! 10-30 recommended)
   - **Duration**: 1-15 seconds (1-2 recommended)
6. Check **"Enable PiShock"**
7. Click **Test** to verify it works (uses current settings)
8. Click **Save**

### Step 3: Test Safely

1. Test on yourself first with intensity 10, duration 1 second
2. Gradually increase to find comfortable levels
3. Test the bonk button from web interface
4. Verify it triggers correctly

## 🎮 How It Works

### Bonk Button Behavior

When someone clicks the **BONK!** button:

1. ✅ **Always plays bonk sound** on your computer
2. ⚡ **If PiShock enabled**: Sends shock/vibrate/beep to device
3. 📊 Logs the event in activity log

### Operation Modes

- **Shock (0)**: Electric shock sensation
- **Vibrate (1)**: Vibration only (safer for testing)
- **Beep (2)**: Just makes sound on device (safest test)

### Intensity Levels

- **0-10**: Very gentle (good for testing)
- **10-30**: Light/mild (recommended starting point)
- **30-50**: Moderate (more noticeable)
- **50-70**: Strong (experienced users only)
- **70-100**: Very strong (**DANGER ZONE - NOT RECOMMENDED**)

### Duration

- **1 second**: Quick tap (recommended)
- **2-3 seconds**: Short burst
- **5+ seconds**: Extended (use with caution)
- **Max 15 seconds** (API limit)

## 🔧 Troubleshooting

### "PiShock trigger failed"

**Check:**
1. Credentials are correct (Username, API Key, Sharecode)
2. Device is online and connected
3. Internet connection is working
4. Sharecode hasn't expired
5. API Key is still valid

### "PiShock is disabled"

- Make sure "Enable PiShock" checkbox is checked
- Click Save after enabling

### Device not responding

1. Check device battery
2. Verify device is paired in PiShock app
3. Test from PiShock website directly
4. Try refreshing sharecode

## 📱 Using from Web Interface

Users clicking the bonk button will see:
- 💥 "BONK!" message
- Sound plays locally
- If PiShock enabled: "⚡ Shock sent!" notification

## 🎵 Custom Bonk Sounds

You can change the bonk sound effect:

1. Place `.wav`, `.mp3`, or `.ogg` files in `static/sounds/`
2. In GUI, go to **Sound Settings**
3. Select your bonk sound from dropdown
4. Click **Set as Bonk Sound**
5. Test with **Play** button

## 🔒 Privacy & Security

- **Never share your API key publicly**
- Sharecodes can be revoked at any time
- Check PiShock dashboard for usage logs
- Revoke sharecodes when done using

## ⚠️ Disclaimers

- Use at your own risk
- This is for consensual adult use only
- Follow all safety guidelines
- The developer is not responsible for misuse
- Always prioritize safety and consent

## 💡 Tips

1. **Start gentle**: Always start with low intensity
2. **Test first**: Test on yourself before others
3. **Use vibrate mode**: Safer for initial testing
4. **Check battery**: Low battery = weaker/inconsistent shocks
5. **Safe word**: Always have a safe word/gesture
6. **Supervision**: Don't leave unattended
7. **Hydration**: Stay hydrated (affects conductivity)

## 🆘 Emergency Stop

If you need to disable PiShock immediately:

1. Open GUI
2. Click **⚡ PiShock Settings**
3. Uncheck **"Enable PiShock"**
4. Click **Save**

Or:

1. Delete `pishock_config.json` file
2. Restart server

## 📚 Additional Resources

- PiShock Official Site: https://pishock.com
- PiShock Discord: Join for support
- API Documentation: Check PiShock website

---

**Remember:** Safety, Consent, and Communication are paramount! 💜

Made with care for responsible kink play.
