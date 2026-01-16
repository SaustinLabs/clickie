# 🌐 Ngrok Setup Guide for Remote Audio Clicker

Ngrok allows friends to access your audio clicker from anywhere on the internet **without port forwarding**! Here's how to get it working:

## 📋 Step 1: Create Free Ngrok Account

1. **Go to ngrok.com** and click "Sign up"
2. **Choose a free account** (works perfectly for our needs)
3. **Verify your email** when they send the confirmation

## 🔑 Step 2: Get Your Auth Token

1. **Log into your ngrok dashboard** at https://dashboard.ngrok.com/
2. **Go to "Your Authtoken"** section (or https://dashboard.ngrok.com/get-started/your-authtoken)
3. **Copy the auth token** - it looks like: `2abc123def456ghi789jkl_1A2B3C4D5E6F7G8H9I0J`

## ⚙️ Step 3: Configure Ngrok with Your Token

### Super Easy Setup (Recommended):
1. **Open `app.py`** in any text editor
2. **Find this line** near the top: `NGROK_AUTH_TOKEN = ""`
3. **Paste your token** between the quotes: `NGROK_AUTH_TOKEN = "your_token_here"`
4. **Save the file**
5. **Run your app** - tunnel will start automatically!

### Manual Setup (Alternative):
If you want to set it up manually:

```powershell
# Install ngrok globally (optional)
pip install pyngrok

# Or just let the app handle it automatically
```

## 🚀 Step 4: Using Your Audio Clicker Publicly

### Starting with Public Access:
```powershell
# Just run the app with your token configured
python app.py

# Or use the batch file (if you updated it)
Start_AudioClicker.bat
```

### What You'll See:
```
🌐 Setting up public access...
🔐 Auth token found, setting up ngrok tunnel...
✅ Public tunnel ready: https://abc123def.ngrok-free.app
🌍 Share this URL with friends: https://abc123def.ngrok-free.app
💡 Friends won't see ngrok warning page - direct access!
```

### ✨ No More Warning Page!
The app automatically includes the `ngrok-skip-browser-warning` header, so your friends will go **directly to your clicker** without seeing ngrok's browser warning page!

## 📱 Step 5: Share with Friends

### Send your friends:
- **The ngrok URL** (like `https://abc123def.ngrok-free.app`)
- **Tell them** it's your remote audio clicker
- **They can click** the button to trigger sounds on your PC!

### For VRChat Users:
- **The OSC will work automatically** when they click
- **Your avatar will react** if you have the right parameters set up
- **Parameters used**: `AudioClicker_Active` (bool) and `AudioClicker_Count` (int)

## 🔧 Technical Details

### Free Ngrok Limits:
- ✅ **1 online tunnel at a time** (perfect for us)
- ✅ **40 connections per minute** (plenty for friends)
- ✅ **No time limits** on tunnel usage
- ✅ **HTTPS encryption** included

### What Happens:
1. **Ngrok creates a secure tunnel** from their servers to your PC
2. **Friends access the public URL** which forwards to your local app
3. **No ports opened** on your router/firewall
4. **All traffic is encrypted** end-to-end

### URL Changes:
- **Free ngrok URLs change** each time you restart
- **To get a static URL**, you'd need a paid plan ($8/month)
- **For friends**: Just send the new URL when you restart

## 🎯 Quick Start Commands

### First Time:
```powershell
cd "C:\Users\HOME\clicker\New folder"
python app.py
# Follow prompts to enter ngrok token
```

### Regular Use:
```powershell
cd "C:\Users\HOME\clicker\New folder"
python app.py
# Just press Enter to use saved settings
```

### Using the Batch File:
```powershell
# The batch file should work automatically now
# Just double-click Start_AudioClicker.bat
# It will detect your token and set up the tunnel
```

## 🔍 Troubleshooting

### "ngrok auth token required":
- **Make sure** you copied the token correctly
- **Go to** https://dashboard.ngrok.com/get-started/your-authtoken
- **Copy the full token** (usually starts with numbers/letters and contains underscores)

### "simultaneous ngrok agent sessions" error:
- **Another ngrok is running!** Free accounts only allow 1 tunnel at a time
- **Quick fix**: `taskkill /F /IM ngrok.exe`
- **Check existing tunnels**: Visit http://localhost:4040
- **Alternative**: Use the existing tunnel if it's pointing to port 5000

### "tunnel failed to start":
- **Check internet connection**
- **Try restarting** the app
- **Make sure** no other ngrok tunnels are running

### "ngrok not found":
- **The app installs it automatically** with `pip install pyngrok`
- **If that fails**, try: `pip install --upgrade pyngrok`

### Friends can't access:
- **Send the exact URL** shown in the console
- **Make sure** they're using `https://` not `http://`
- **The URL changes** each time you restart the app

## 🎮 VRChat Integration

### Avatar Setup:
Your avatar needs these parameters for OSC to work:
- **AudioClicker_Active** (Bool) - Shows when clicked
- **AudioClicker_Count** (Int) - Shows total clicks

### OSC Testing:
- **Start VRChat** with OSC enabled
- **Have a friend click** the web button
- **Check if your avatar reacts** (parameter changes)

## 💡 Pro Tips

### For Regular Use:
- **Keep the console window open** to see the ngrok URL
- **Bookmark the URL** while using (changes on restart)
- **Share the URL** via Discord/text to friends

### For Streaming:
- **Hide the auth token** from stream (cover console during setup)
- **The public URL is safe** to show on stream
- **Consider LocalTunnel** as an alternative (no signup required)

## 🆚 Ngrok vs LocalTunnel

### Ngrok (Recommended):
- ✅ **More reliable** and faster
- ✅ **Better error handling**
- ✅ **HTTPS by default**
- ❌ Requires account/token

### LocalTunnel (Alternative):
- ✅ **No signup required**
- ✅ **Works immediately**
- ❌ **Less reliable** connection
- ❌ **URLs can be weird** (like `https://tiny-rats-123.loca.lt`)

---

## 🎉 You're All Set!

Once you have your ngrok token configured, your Audio Clicker will be accessible to friends worldwide! The app handles all the technical details automatically.

**Questions?** Check the console output - it shows exactly what URLs to share and any error messages if something goes wrong.